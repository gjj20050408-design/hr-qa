"""问答质量闭环服务 — 聚合"未命中/低分"问题，并借助 LLM 生成 FAQ 草稿

把系统里割裂的数据串成闭环：
  qa_records（用户真实提问） + feedback（评价） → 找出答得不好的高频问题
  → LLM 依据现有制度文档生成 FAQ 草稿 → HR 审核后发布为正式 FAQ
"""
import logging
from typing import Optional

from sqlalchemy import select, func, or_, Integer, cast
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.qa_record import QARecord
from app.models.document import Document
from app.enums.enums import AnswerType, FeedbackType, DocStatus

logger = logging.getLogger(__name__)


class QAInsightService:

    @staticmethod
    async def get_faq_candidates(
        db_session: AsyncSession, limit: int = 10, min_count: int = 1,
    ) -> list[dict]:
        """聚合"待优化问题"：答不出（no_result）或被判为无帮助（not_helpful）的提问，
        按问题文本归并后按出现次数倒序返回。

        归并用 TRIM+LOWER 归一化，避免大小写/空白导致同一问题被拆散。
        """
        norm_q = func.lower(func.trim(QARecord.question))

        # 命中"待优化"的条件：答不出 或 用户明确点了没帮助
        condition = or_(
            QARecord.answer_type == AnswerType.NO_RESULT,
            QARecord.feedback == FeedbackType.NOT_HELPFUL,
        )

        query = (
            select(
                norm_q.label("norm_question"),
                func.count(QARecord.record_id).label("cnt"),
                func.max(QARecord.question).label("sample_question"),
                func.max(QARecord.created_at).label("last_asked"),
                func.sum(cast(QARecord.answer_type == AnswerType.NO_RESULT, Integer)).label("no_result_count"),
                func.sum(cast(QARecord.feedback == FeedbackType.NOT_HELPFUL, Integer)).label("not_helpful_count"),
            )
            .where(condition)
            .group_by(norm_q)
            .having(func.count(QARecord.record_id) >= min_count)
            .order_by(func.count(QARecord.record_id).desc(), func.max(QARecord.created_at).desc())
            .limit(limit)
        )
        result = await db_session.execute(query)
        rows = result.all()

        return [
            {
                "question": r.sample_question,
                "count": r.cnt,
                "no_result_count": int(r.no_result_count or 0),
                "not_helpful_count": int(r.not_helpful_count or 0),
                "last_asked": str(r.last_asked) if r.last_asked else None,
            }
            for r in rows
        ]

    SYSTEM_PROMPT = (
        "你是企业 HR 知识库助理。请根据提供的【制度文档片段】，为员工的【问题】撰写一条 FAQ。"
        "要求：\n"
        "1. 严格依据文档内容作答，不得编造文档中没有的规定；\n"
        "2. 答案简明、分点、可直接展示给员工；\n"
        "3. 若文档片段不足以回答，answer 字段填\"暂无足够制度依据，需人工补充\"；\n"
        "4. 只输出 JSON，格式：{\"question\": \"规范化后的问题\", \"answer\": \"标准答案\", "
        "\"keywords\": \"逗号分隔的关键词\"}"
    )

    @staticmethod
    async def generate_faq_draft(
        question: str, db_session: AsyncSession,
    ) -> Optional[dict]:
        """依据现有制度文档，用 LLM 生成 FAQ 草稿（不落库，供 HR 审核）。

        返回 {question, answer, keywords, related_doc_id, _model}；LLM 不可用时返回 None。
        """
        from app.providers.llm import llm_provider
        from app.utils.llm_json import parse_llm_json

        # 先按关键词检索已发布制度文档，作为 LLM 的事实依据（避免臆造）
        related_doc_id = None
        context_chunks = []
        kw = f"%{question.strip()}%"
        try:
            result = await db_session.execute(
                select(Document)
                .where(
                    Document.status == DocStatus.PUBLISHED,
                    or_(Document.title.like(kw), Document.content.like(kw)),
                )
                .limit(3)
            )
            docs = result.scalars().all()
            for d in docs:
                content = (d.content or "")[:1500]
                context_chunks.append(f"《{d.title}》\n{content}")
                if related_doc_id is None:
                    related_doc_id = d.document_id
        except Exception as e:
            logger.warning(f"QAInsight: 检索制度文档失败: {e}")

        context_text = "\n\n---\n\n".join(context_chunks) if context_chunks else "（未检索到相关制度文档）"

        # 校验 LLM 可用
        try:
            if not llm_provider.health_check():
                logger.info("QAInsight: LLM 不可用，无法生成草稿")
                return None
        except Exception:
            return None

        prompt = (
            f"【问题】\n{question}\n\n"
            f"【制度文档片段】\n{context_text}\n\n"
            "请按系统要求输出 FAQ 的 JSON。"
        )
        try:
            resp = llm_provider.generate(
                prompt=prompt,
                system_prompt=QAInsightService.SYSTEM_PROMPT,
                max_tokens=1024,
                temperature=0.2,
            )
            if not resp.content or resp.content.startswith("[LLM"):
                return None
            data = parse_llm_json(resp.content)
            if data is None:
                logger.warning(f"QAInsight: 解析 LLM 输出失败: {resp.content[:200]}")
                return None
            return {
                "question": data.get("question") or question,
                "answer": data.get("answer", ""),
                "keywords": data.get("keywords", ""),
                "related_doc_id": related_doc_id,
                "_model": resp.model,
            }
        except Exception as e:
            logger.error(f"QAInsight: 生成草稿失败: {e}")
            return None
