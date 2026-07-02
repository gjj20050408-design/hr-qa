"""问答策略链 — 责任链模式实现

完整策略链: FAQ匹配 → 规则匹配 → 个人数据守卫 → 权限过滤 → 全文搜索 → RAG智能问答 → 兜底
"""
import re
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List

import jieba
from sqlalchemy import select, func, or_, desc
from sqlalchemy.dialects.mysql import match
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.enums import Role, AnswerType, FAQStatus, DocStatus, AccessLevel, SensitivityLevel, QueryType
from app.enums.constants import (
    RULE_TEMPLATES, QA_THRESHOLDS, DEFAULT_USER_CONTEXT,
    PERMISSION_MATRIX, DOC_TO_ACCESS_MAP,
)
from app.models.faq import FAQ
from app.models.document import Document
from app.models.employee_data_sensitivity import EmployeeDataSensitivity
from app.utils.snippet import generate_snippet, similarity_chinese
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


@dataclass
class QAContext:
    """策略链中传递的上下文对象"""
    question: str
    processed_question: str = ""
    user_id: str = ""
    user_role: Role = Role.EMPLOYEE
    user_context: dict = field(default_factory=dict)
    session_id: str = ""
    history: list = field(default_factory=list)   # 多轮追问：历史对话 messages
    answer: Optional[str] = None
    answer_type: Optional[AnswerType] = None
    reference_docs: list = field(default_factory=list)
    confidence: Optional[float] = None
    filtered_doc_ids: list = field(default_factory=list)
    personal_data_extraction: Optional[dict] = None   # ★二期
    personal_data_allowed: list = field(default_factory=list)
    personal_data_denied: list = field(default_factory=list)
    is_done: bool = False


class QAHandler(ABC):
    """责任链模式中的抽象处理器"""

    def __init__(self):
        self._next: Optional["QAHandler"] = None

    def set_next(self, handler: "QAHandler") -> "QAHandler":
        self._next = handler
        return handler

    @abstractmethod
    async def handle(self, ctx: QAContext, db_session: AsyncSession) -> QAContext:
        ...

    async def handle_next(self, ctx: QAContext, db_session: AsyncSession) -> QAContext:
        if self._next and not ctx.is_done:
            return await self._next.handle(ctx, db_session)
        return ctx


class FAQMatcher(QAHandler):
    """② FAQ匹配处理器"""

    async def handle(self, ctx: QAContext, db_session: AsyncSession) -> QAContext:
        keywords = " ".join(jieba.cut(ctx.processed_question))
        result = await db_session.execute(
            select(FAQ).where(
                FAQ.status == FAQStatus.ACTIVE,
                match(FAQ.question, FAQ.keywords, against=keywords),
            ).limit(5)
        )
        faqs = result.scalars().all()

        best, best_score = None, 0.0
        for faq in faqs:
            score = similarity_chinese(ctx.processed_question, faq.question)
            if score > best_score:
                best_score = score
                best = faq

        if best and best_score >= QA_THRESHOLDS["faq_similarity_min"]:
            best.view_count = (best.view_count or 0) + 1
            ctx.answer = best.answer
            ctx.answer_type = AnswerType.FAQ
            ctx.reference_docs = [{"doc_id": best.related_doc_id, "title": "FAQ标准答案"}]
            ctx.confidence = best_score
            ctx.is_done = True
        return await self.handle_next(ctx, db_session)

    @staticmethod
    def _similarity(q1: str, q2: str) -> float:
        """FAQ 中文相似度（委托至公共工具模块）"""
        return similarity_chinese(q1, q2)


class RuleMatcher(QAHandler):
    """③ 规则匹配处理器"""

    async def handle(self, ctx: QAContext, db_session: AsyncSession) -> QAContext:
        for rule in RULE_TEMPLATES:
            for pattern in rule["patterns"]:
                if re.search(pattern, ctx.processed_question):
                    template = rule["template"]
                    if rule.get("requires_user_context"):
                        template = self._fill_context(template, ctx.user_context)
                    ctx.answer = template
                    ctx.answer_type = AnswerType.RULE
                    ctx.confidence = 0.90
                    ctx.is_done = True
                    return ctx
        return await self.handle_next(ctx, db_session)

    @staticmethod
    def _fill_context(template: str, uctx: dict) -> str:
        result = template
        if "{tenure_years}" in result and uctx.get("hire_date"):
            hire = uctx["hire_date"]
            if isinstance(hire, str):
                hire = datetime.strptime(hire, "%Y-%m-%d").date() if "-" in str(hire) else datetime.strptime(str(hire), "%Y-%m-%d").date()
            years = datetime.now(timezone.utc).date().year - hire.year
            result = result.replace("{tenure_years}", str(years))
        if "{annual_leave_days}" in result and uctx.get("hire_date"):
            hire = uctx["hire_date"]
            if isinstance(hire, str):
                hire = datetime.strptime(hire, "%Y-%m-%d").date() if "-" in str(hire) else datetime.strptime(str(hire), "%Y-%m-%d").date()
            years = datetime.now(timezone.utc).date().year - hire.year
            days = 5 if years < 3 else (10 if years < 10 else 15)
            result = result.replace("{annual_leave_days}", str(days))
        return result


class PermissionFilter(QAHandler):
    """④ 权限过滤处理器 — 横切关注点，注解上下文"""

    async def handle(self, ctx: QAContext, db_session: AsyncSession) -> QAContext:
        return await self.handle_next(ctx, db_session)

    @staticmethod
    async def filter_documents(docs: list, role: Role, ctx: "QAContext" = None, db_session: AsyncSession = None) -> tuple:
        allowed, filtered = [], []
        for doc in docs:
            if doc.can_access(role):
                allowed.append(doc)
            else:
                filtered.append(doc)
        # 审计日志：记录权限过滤事件
        if filtered and ctx and db_session:
            try:
                await AuditService.create_log(
                    user_id=ctx.user_id,
                    action="permission_filtered",
                    resource_type="document",
                    resource_id="qa_search",
                    detail=json.dumps({
                        "total_retrieved": len(docs),
                        "filtered_count": len(filtered),
                        "allowed_count": len(allowed)
                    }),
                    db_session=db_session,
                )
            except Exception:
                pass  # 审计失败不影响主流程
        return allowed, filtered


class SearchHandler(QAHandler):
    """⑤ 全文搜索处理器 — 收集候选文档，不阻断链路，交由 RAG 生成自然语言"""

    SEARCH_RESULTS_KEY = "_search_snippets"

    async def handle(self, ctx: QAContext, db_session: AsyncSession) -> QAContext:
        from sqlalchemy.orm import selectinload
        kw = f"%{ctx.processed_question}%"
        result = await db_session.execute(
            select(Document).options(selectinload(Document.category)).where(
                Document.status == DocStatus.PUBLISHED,
                or_(
                    Document.title.like(kw),
                    Document.content.like(kw),
                ),
            ).limit(QA_THRESHOLDS["search_max_results"])
        )
        docs = result.scalars().all()

        allowed, filtered = await PermissionFilter.filter_documents(docs, ctx.user_role, ctx, db_session)
        ctx.filtered_doc_ids = [d.document_id for d in filtered]

        if allowed:
            snippets = []
            for doc in allowed:
                snippet = generate_snippet(doc.content, ctx.processed_question)
                snippets.append({
                    "document_id": doc.document_id,
                    "title": doc.title,
                    "snippet": snippet,
                    "category": doc.category.name if doc.category else "",
                    "version": doc.version,
                })
            # 搜索结果存入上下文供后续处理器（如 RAG）参考，不阻断链路
            setattr(ctx, self.SEARCH_RESULTS_KEY, snippets)
            # reference_docs 预先填充，RAG 可覆盖
            ctx.reference_docs = [{"doc_id": s["document_id"], "title": s["title"], "section": s["snippet"][:100]} for s in snippets]

        # 继续传递到下一个处理器（RAG），不在此处终止链路
        return await self.handle_next(ctx, db_session)


class RAGHandler(QAHandler):
    """⑥ RAG智能问答处理器

    流程：阿里云Embedding → 本地向量库检索 → 权限过滤 → DeepSeek生成回答
    向量化用阿里云API，向量存本地SQLite，理解生成用DeepSeek。
    """

    RAG_SYSTEM_PROMPT = (
        "你是企业HR制度智能助手。请根据以下制度文档内容回答问题。\n"
        "要求：\n"
        "1. 仅基于提供的文档内容回答，不要编造信息\n"
        "2. 在回答末尾注明引用来源（文档标题）\n"
        "3. 如果文档内容不足以回答，请明确说明\n"
        "4. 回答应简洁专业，使用中文"
    )

    async def handle(self, ctx: QAContext, db_session: AsyncSession) -> QAContext:
        if ctx.is_done:
            return await self.handle_next(ctx, db_session)

        # 检查LLM是否可用
        from app.providers.llm import llm_provider
        from app.providers.embedding import embedding_provider
        from app.providers.vector_store import vector_store

        if isinstance(llm_provider, type(None)):
            return await self.handle_next(ctx, db_session)

        # LLM健康检查
        try:
            if not llm_provider.health_check():
                logger.info("LLM health check failed, skipping RAG")
                return await self.handle_next(ctx, db_session)
        except Exception:
            return await self.handle_next(ctx, db_session)

        try:
            # Step 1: 问题向量化（阿里云 text-embedding-v3）
            # 多轮追问检索增强：纯追问（如"那病假呢"）向量化效果差，
            # 拼接上一轮的用户问题后再检索（仅用于检索，不改变喂给 LLM 的 ctx.question）
            retrieval_query = ctx.processed_question
            if ctx.history:
                last_user_q = next(
                    (m["content"] for m in reversed(ctx.history) if m.get("role") == "user"),
                    "",
                )
                if last_user_q:
                    retrieval_query = f"{last_user_q} {ctx.processed_question}"
            query_embedding = embedding_provider.embed(retrieval_query)
            if not query_embedding:
                return await self.handle_next(ctx, db_session)

            # Step 2: 本地向量库检索（SQLite + 余弦相似度）
            top_k = QA_THRESHOLDS.get("rag_top_k_retrieval", 10)
            chunks = vector_store.query(query_embedding, top_k)

            if not chunks:
                return await self.handle_next(ctx, db_session)

            # Step 3: 权限过滤 - 加载文档并检查权限
            doc_ids = list(set(c.document_id for c in chunks))
            if doc_ids:
                from sqlalchemy.orm import selectinload
                result = await db_session.execute(
                    select(Document).options(selectinload(Document.category)).where(Document.document_id.in_(doc_ids))
                )
                docs = {d.document_id: d for d in result.scalars().all()}

                allowed_chunks = []
                for chunk in chunks:
                    doc = docs.get(chunk.document_id)
                    if doc and doc.can_access(ctx.user_role):
                        allowed_chunks.append(chunk)

                if not allowed_chunks:
                    ctx.filtered_doc_ids = doc_ids
                    ctx.answer = "🔒 该内容需要HR权限才能查看。如有疑问，请联系HR部门（hr@company.com）"
                    ctx.answer_type = AnswerType.NO_RESULT
                    ctx.confidence = 0.0
                    ctx.is_done = True
                    return ctx
            else:
                allowed_chunks = chunks
                docs = {}

            # Step 4: 构建上下文提示（取Top-N个chunk）
            n_prompt = min(QA_THRESHOLDS.get("rag_top_n_prompt", 5), len(allowed_chunks))
            context_parts = []
            for i, chunk in enumerate(allowed_chunks[:n_prompt]):
                doc = docs.get(chunk.document_id) if doc_ids else None
                title = doc.title if doc else f"文档-{chunk.document_id[:8]}"
                content = (chunk.content or "")[:800]
                context_parts.append(f"[来源{i+1}: {title}]\n{content}")

            context_text = "\n\n---\n\n".join(context_parts)

            prompt = (
                f"请根据以下制度文档内容回答问题。\n\n"
                f"【问题】\n{ctx.question}\n\n"
                f"【参考文档】\n{context_text}\n\n"
                f"请给出准确、专业的回答，并引用来源。"
            )

            # Step 5: 调用 DeepSeek 生成回答
            # [临时调试] 确认多轮追问历史是否带入，验证后删除
            logger.info(
                f"[RAG-DEBUG] session={ctx.session_id[:8]} "
                f"history_rounds={len(ctx.history) // 2} "
                f"question={ctx.question!r} retrieval_query={retrieval_query!r}"
            )

            llm_response = llm_provider.generate(
                prompt=prompt,
                system_prompt=self.RAG_SYSTEM_PROMPT,
                max_tokens=2048,
                temperature=0.3,
                history=ctx.history,   # 多轮追问：携带历史对话
            )

            if not llm_response.content or llm_response.content.startswith("[LLM"):
                return await self.handle_next(ctx, db_session)

            ctx.answer = llm_response.content
            ctx.answer_type = AnswerType.RAG
            ctx.reference_docs = [
                {
                    "doc_id": c.document_id,
                    "title": docs.get(c.document_id).title if docs.get(c.document_id) else f"文档-{c.document_id[:8]}",
                    "section": (c.content or "")[:100],
                }
                for c in allowed_chunks[:n_prompt]
            ]
            ctx.confidence = 0.85 if llm_response.content else 0.5
            ctx.is_done = True

        except Exception as e:
            logger.warning(f"RAG handler failed, falling through: {e}")

        return await self.handle_next(ctx, db_session)


class PersonalDataGuard(QAHandler):
    """⑦ 个人数据访问守卫（Phase 4）

    通过LLM意图提取 + 数据库字段配置，控制个人敏感数据的访问。
    核心逻辑：
    - 识别问题是否涉及个人数据查询
    - 如果是，检查敏感度层级
    - private: 仅本人+HR可查
    - department: 同部门可查
    - public: 全员可查
    - aggregation: 聚合查询（平均/排名/统计）一律拒绝
    - HR/admin: 全局放行
    """

    # 4种拒绝模板 — 与PRD FR-10.3/FR-1.7 一字不差
    DENIAL_ALL_PRIVATE = (
        "🔒 抱歉，您无权查询{name}的{fields}等个人私密信息。"
        "如需了解自己的权益，请尝试询问「我的{example_field}是多少」"
    )
    DENIAL_CROSS_DEPARTMENT = (
        "🔒 抱歉，{name}与您不在同一部门，您无权查询其{fields}等信息。"
        "如需了解自己的权益，请尝试询问「我的{example_field}是什么」"
    )
    DENIAL_AGGREGATION = (
        "🔒 抱歉，出于数据安全考虑，系统不支持聚合统计类查询"
        "（如平均值、排名、人数统计等）。如有业务需要，请联系HR部门。"
    )
    DENIAL_EXTRACTION_FAILED = (
        "🔒 抱歉，无法确认您在查询哪位员工的信息。"
        "请使用明确姓名后重试，例如「张三的工龄是多少」。"
        "如需查询自己，请使用「我的…」句式。"
    )

    async def handle(self, ctx: QAContext, db_session: AsyncSession) -> QAContext:
        if ctx.is_done:
            return await self.handle_next(ctx, db_session)

        # HR/admin 全局放行 (PRD D2)
        if ctx.user_role in (Role.HR_SPECIALIST, Role.ADMIN):
            return await self.handle_next(ctx, db_session)

        # Step 1: LLM意图提取 (PRD D4: LLM提取 + 数据库校验双重验证)
        extraction = await self._extract_intent(ctx, db_session)
        ctx.personal_data_extraction = extraction

        # Step 2: 主审核逻辑
        return await self._audit(ctx, extraction, db_session)

    async def _extract_intent(self, ctx: QAContext, db_session: AsyncSession) -> dict:
        """LLM意图提取 — 输出JSON (PRD FR-10.3 附录B)

        返回 dict: {query_type, target_persons, requested_fields, is_self_query, confidence}
        失败时返回 confidence=0 的保守结果 (AC-NFR-07: 失败保守拒绝)
        """
        # 默认保守结果
        conservative = {
            "query_type": "personal_data",
            "target_persons": [],
            "requested_fields": [],
            "is_self_query": False,
            "confidence": 0.0,
        }

        # 构建当前用户信息 (PRD 附录B: System Prompt 包含用户上下文)
        user_name = ctx.user_context.get("name", "未知")
        user_emp_id = ctx.user_context.get("employee_id", "未知")
        user_dept = ctx.user_context.get("department", "未知")
        user_role = ctx.user_role.value if hasattr(ctx.user_role, "value") else str(ctx.user_role)

        system_prompt = (
            "你是一个HR数据查询分析器。你的任务是从用户问题中提取查询意图，而不是回答问题。\n\n"
            f"当前登录用户信息：\n"
            f"- 姓名：{user_name}\n"
            f"- 工号：{user_emp_id}\n"
            f"- 部门：{user_dept}\n"
            f"- 角色：{user_role}\n\n"
            "分析规则：\n"
            "1. 如果用户使用「我」「我的」等第一人称，目标人物默认为当前登录用户\n"
            "2. 如果用户明确提到其他人名（非当前用户），目标人物为提及的人名\n"
            "3. 如果用户使用「我下属」「我领导」等，需提取关系链中的具体目标人物\n"
            "4. 如果问题涉及平均值、最高、最低、总共、多少人、有哪些人等，标记为聚合查询\n"
            "5. 仅提取问题中明确请求的数据字段（工龄、工资、绩效、部门等）\n"
            "6. 如果无法确定目标人物，confidence应低于0.7\n\n"
            "输出JSON格式（不要输出其他内容）：\n"
            "{\n"
            '  "query_type": "personal_data|policy_only|mixed|aggregation|chitchat",\n'
            '  "target_persons": ["目标人物姓名"],\n'
            '  "requested_fields": ["字段中文名"],\n'
            '  "is_self_query": true|false,\n'
            '  "confidence": 0.0~1.0\n'
            "}\n\n"
            "query_type 说明：\n"
            "- personal_data: 查询具体员工的个人数据（工龄、工资、绩效等）\n"
            "- policy_only: 查询公司制度/政策（考勤、年假规定、报销流程等）\n"
            "- mixed: 既查个人数据又涉及制度\n"
            "- aggregation: 聚合统计类查询（平均、最高、多少人等）\n"
            "- chitchat: 闲聊、问候、身份询问（如你是谁/你好/谢谢等非业务查询）\n"
            "对于 chitchat 类型，confidence 设为 1.0，target_persons 和 requested_fields 为空。"
        )

        try:
            from app.providers.llm import llm_provider
            # 检查LLM可用性
            if isinstance(llm_provider, type(None)) or not llm_provider.health_check():
                logger.warning("PersonalDataGuard: LLM not available, using conservative denial")
                return conservative

            user_prompt = f"用户问题：{ctx.question}"
            resp = llm_provider.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=2048,
                temperature=0,
            )

            content = resp.content.strip() if resp.content else ""
            if not content or content.startswith("[LLM"):
                logger.warning("PersonalDataGuard: LLM returned empty/error response")
                return conservative

            # 解析JSON
            extraction = self._parse_llm_json(content)
            if extraction is None:
                logger.warning(f"PersonalDataGuard: failed to parse LLM JSON: {content[:200]}")
                return conservative

            # 标准化字段
            extraction.setdefault("query_type", "personal_data")
            extraction.setdefault("target_persons", [])
            extraction.setdefault("requested_fields", [])
            extraction.setdefault("is_self_query", False)
            extraction.setdefault("confidence", 0.0)

            # 确保类型正确
            try:
                extraction["confidence"] = float(extraction["confidence"])
            except (ValueError, TypeError):
                extraction["confidence"] = 0.0

            if not isinstance(extraction["target_persons"], list):
                extraction["target_persons"] = []
            if not isinstance(extraction["requested_fields"], list):
                extraction["requested_fields"] = []

            logger.info(
                f"PersonalDataGuard extraction: query_type={extraction['query_type']}, "
                f"targets={extraction['target_persons']}, fields={extraction['requested_fields']}, "
                f"is_self={extraction['is_self_query']}, conf={extraction['confidence']}"
            )
            return extraction

        except Exception as e:
            logger.error(f"PersonalDataGuard: LLM intent extraction failed: {e}")
            return conservative

    @staticmethod
    def _parse_llm_json(content: str) -> Optional[dict]:
        """从LLM响应中解析JSON（委托至公共工具模块）"""
        from app.utils.llm_json import parse_llm_json
        return parse_llm_json(content)

    async def _audit(self, ctx: QAContext, extraction: dict, db_session: AsyncSession) -> QAContext:
        """主审核方法 (PRD FR-10.3 审核流程)

        - query_type == "policy_only" → 直接放行
        - query_type == "aggregation" → 立即拒绝
        - confidence < 0.7 → 保守拒绝
        - 否则调用字段级校验
        """
        query_type = extraction.get("query_type", "personal_data")
        confidence = extraction.get("confidence", 0.0)

        # 纯制度咨询 → 跳过个人数据审核
        if query_type == QueryType.POLICY_ONLY.value:
            logger.info("PersonalDataGuard: policy_only, bypassing")
            return await self.handle_next(ctx, db_session)

        # 闲聊/问候/身份询问 → 跳过个人数据审核，交由后续环节处理
        if query_type == QueryType.CHITCHAT.value:
            logger.info(f"PersonalDataGuard: chitchat, bypassing: {ctx.question[:80]}")
            return await self.handle_next(ctx, db_session)

        # 聚合查询 → 立即拒绝 (PRD D5)
        if query_type == QueryType.AGGREGATION.value:
            logger.info(f"PersonalDataGuard: aggregation denied for question: {ctx.question[:80]}")
            ctx.answer = self.DENIAL_AGGREGATION
            ctx.answer_type = AnswerType.NO_RESULT
            ctx.confidence = 1.0
            ctx.is_done = True
            await self._log_denial(ctx, extraction, "aggregation", [], db_session)
            return ctx

        # 置信度不足 → 保守拒绝 (PRD D6: confidence < 0.7)
        if confidence < 0.7:
            logger.info(f"PersonalDataGuard: low confidence ({confidence}), conservative denial")
            ctx.answer = self.DENIAL_EXTRACTION_FAILED
            ctx.answer_type = AnswerType.NO_RESULT
            ctx.confidence = 1.0
            ctx.is_done = True
            await self._log_denial(ctx, extraction, "extraction_failed", [], db_session)
            return ctx

        # 有目标人物 → 逐字段校验
        target_persons = extraction.get("target_persons", [])
        requested_fields = extraction.get("requested_fields", [])
        is_self_query = extraction.get("is_self_query", False)

        if not target_persons or not requested_fields:
            return await self.handle_next(ctx, db_session)

        return await self._check_fields(ctx, extraction, target_persons, requested_fields, is_self_query, db_session)

    async def _check_fields(
        self, ctx: QAContext, extraction: dict,
        target_persons: list, requested_fields: list,
        is_self_query: bool, db_session: AsyncSession,
    ) -> QAContext:
        """逐字段校验 (PRD §8.2 权限判定逻辑)

        - HR/admin → 全部放行 (已在 handle 中处理)
        - is_self_query → 全部放行
        - 对每个字段查 EmployeeDataSensitivity 表获取 sensitivity_level
        - public → 放行
        - private → 拒绝（非本人）
        - department → 查询 user 表 department_id，相同则放行，不同则拒绝
        - 填充 ctx.personal_data_allowed 和 ctx.personal_data_denied
        """
        # 加载敏感度配置
        result = await db_session.execute(
            select(EmployeeDataSensitivity).where(EmployeeDataSensitivity.is_active == True)
        )
        rows = result.scalars().all()
        sensitivity_map = {s.field_label: s for s in rows}
        # 同时按 field_name 索引
        sensitivity_map.update({s.field_name: s for s in rows})

        if not sensitivity_map:
            return await self.handle_next(ctx, db_session)

        # 本人查询 → 全部放行 (PRD §8.2: querier == target)
        if is_self_query:
            ctx.personal_data_allowed = requested_fields
            logger.info("PersonalDataGuard: self-query, all fields allowed")
            return await self.handle_next(ctx, db_session)

        # 查询他人 → 逐字段校验
        denied = []
        allowed = []

        # 按目标人物分组检查
        for target_name in target_persons:
            for field_cn in requested_fields:
                config = sensitivity_map.get(field_cn)
                if not config:
                    # 字段未在敏感度表中配置 → 放行（由后续数据库查询兜底）
                    allowed.append({"person": target_name, "field": field_cn})
                    continue

                level = config.sensitivity_level

                if level == SensitivityLevel.PUBLIC:
                    # 全员可见 → 放行
                    allowed.append({"person": target_name, "field": field_cn})

                elif level == SensitivityLevel.PRIVATE:
                    # 绝对私密 → 拒绝（非本人已排除，此处必然是查他人）
                    denied.append({"person": target_name, "field": field_cn, "level": "private"})

                elif level == SensitivityLevel.DEPARTMENT:
                    # 部门内可见 → 查询数据库判断是否同部门
                    same_dept = await self._check_same_department(ctx, target_name, db_session)
                    if same_dept:
                        allowed.append({"person": target_name, "field": field_cn})
                    else:
                        denied.append({"person": target_name, "field": field_cn, "level": "department"})

        # 填充上下文
        ctx.personal_data_allowed = allowed
        ctx.personal_data_denied = denied

        # 全部被拒 → 拦截 (PRD: 全部拒绝 → 不调用LLM，返回权限提示)
        if not allowed and denied:
            return await self._build_denial_response(ctx, extraction, denied, db_session)

        # 有放行字段 → 继续
        if denied:
            logger.info(f"PersonalDataGuard: partial denial, allowed={len(allowed)}, denied={len(denied)}")

        return await self.handle_next(ctx, db_session)

    async def _check_same_department(self, ctx: QAContext, target_name: str, db_session: AsyncSession) -> bool:
        """查询数据库判断查询者与目标人物是否同部门 (PRD §8.2)"""
        from app.models.user import User
        try:
            # 查询目标人物的 department_id
            result = await db_session.execute(
                select(User.department_id).where(User.name == target_name)
            )
            target_dept_id = result.scalar()
            if not target_dept_id:
                logger.warning(f"PersonalDataGuard: target '{target_name}' not found in users table")
                return False

            # 查询者 department_id 从 ctx.user_context 中获取
            querier_dept = ctx.user_context.get("department", "")
            # 也需要查数据库获取 department_id（ctx.user_context 中存储的是 department name）
            # 查询查询者的 department_id
            result2 = await db_session.execute(
                select(User.department_id).where(User.user_id == ctx.user_id)
            )
            querier_dept_id = result2.scalar()

            same = querier_dept_id and target_dept_id and querier_dept_id == target_dept_id
            logger.info(
                f"PersonalDataGuard: same_department check: "
                f"querier_dept_id={querier_dept_id}, target_dept_id={target_dept_id}, same={same}"
            )
            return same
        except Exception as e:
            logger.error(f"PersonalDataGuard: same_department check failed: {e}")
            return False

    async def _build_denial_response(
        self, ctx: QAContext, extraction: dict, denied: list, db_session: AsyncSession,
    ) -> QAContext:
        """构建拒绝响应，使用PRD精确模板 (FR-1.7)"""
        # 收集拒绝字段和类型
        private_fields = []
        dept_fields = []
        target_name = denied[0]["person"] if denied else "该员工"

        for d in denied:
            field_label = d["field"]
            if d["level"] == "private":
                private_fields.append(field_label)
            elif d["level"] == "department":
                dept_fields.append(field_label)

        if private_fields:
            # 全部私密拒绝模板
            field_str = "/".join(private_fields)
            example = private_fields[0] if private_fields else "工龄"
            ctx.answer = self.DENIAL_ALL_PRIVATE.format(
                name=target_name, fields=field_str, example_field=example
            )
        elif dept_fields:
            # 跨部门拒绝模板
            field_str = "/".join(dept_fields)
            example = dept_fields[0] if dept_fields else "工龄"
            ctx.answer = self.DENIAL_CROSS_DEPARTMENT.format(
                name=target_name, fields=field_str, example_field=example
            )

        ctx.answer_type = AnswerType.NO_RESULT
        ctx.confidence = 1.0
        ctx.is_done = True

        # 记录拒绝日志 (AC-NFR-04)
        await self._log_denial(ctx, extraction, "all_fields_denied", denied, db_session)

        return ctx

    async def _log_denial(
        self, ctx: QAContext, extraction: dict, reason: str, denied: list, db_session: AsyncSession,
    ) -> None:
        """记录拒绝事件到审计日志 (AC-NFR-04: 拒绝事件日志)"""
        try:
            from app.models.audit_log import AuditLog

            log_entry = AuditLog(
                user_id=ctx.user_id,
                action="personal_data_denied",
                resource_type="personal_data",
                resource_id="",
                detail={
                    "reason": reason,
                    "extraction": extraction,
                    "denied": denied,
                },
                ip_address="",
            )
            db_session.add(log_entry)
            await db_session.flush()
            logger.info(f"PersonalDataGuard: denial logged for user={ctx.user_id}, reason={reason}")
        except Exception as e:
            logger.error(f"PersonalDataGuard: failed to log denial: {e}")


class FallbackHandler(QAHandler):
    """⑧ 最终兜底处理器"""

    async def handle(self, ctx: QAContext, db_session: AsyncSession) -> QAContext:
        if not ctx.is_done:
            if ctx.filtered_doc_ids and not ctx.reference_docs:
                ctx.answer = "🔒 该内容需要HR权限才能查看。如有疑问，请联系HR部门（hr@company.com）"
            else:
                ctx.answer = "未找到相关制度，建议联系HR部门获取帮助。"
            ctx.answer_type = AnswerType.NO_RESULT
            ctx.is_done = True
        return ctx


class QAOrchestrator:
    """问答编排器 — 构建并执行完整策略链"""

    def __init__(self, phase: str = "phase2"):
        self.phase = phase
        self._chain: Optional[QAHandler] = None

    def build_chain(self) -> QAHandler:
        faq = FAQMatcher()           # ① FAQ匹配
        rule = RuleMatcher()         # ② 规则匹配
        data_guard = PersonalDataGuard()  # ③ 个人数据守卫（PRD: 个人数据审核在前）
        perm_filter = PermissionFilter()  # ④ 权限过滤（横切）
        search = SearchHandler()     # ⑤ 全文搜索
        rag = RAGHandler()           # ⑥ RAG智能问答
        fallback = FallbackHandler() # ⑦ 兜底

        faq.set_next(rule)
        rule.set_next(data_guard)
        data_guard.set_next(perm_filter)
        perm_filter.set_next(search)
        search.set_next(rag)
        rag.set_next(fallback)

        self._chain = faq
        return faq

    async def ask(
        self, question: str, user, session_id: str, db_session: AsyncSession
    ) -> QAContext:
        ctx = QAContext(
            question=question,
            processed_question=self._preprocess(question),
            user_id=user.user_id,
            user_role=user.role,
            user_context={
                "hire_date": user.hire_date,
                "job_level": user.job_level,
                "marital_status": user.marital_status.value if user.marital_status else None,
                "name": user.name,
                "employee_id": user.employee_id,
                "department": user.department.name if user.department else "",
            },
            session_id=session_id,
            history=await self._load_history(
                session_id, user.user_id, db_session,
                max_rounds=QA_THRESHOLDS.get("rag_history_max_rounds", 5),
            ),
        )
        handler = self._chain or self.build_chain()
        return await handler.handle(ctx, db_session)

    @staticmethod
    async def _load_history(
        session_id: str, user_id: str, db_session: AsyncSession, max_rounds: int = 5,
    ) -> list:
        """按 session_id 加载最近 max_rounds 轮历史对话，展开为 LLM messages。

        当前问题此时尚未入库，因此只会取到"之前"的记录。跳过权限拒绝类回答
        （以 🔒 开头），避免把拒绝话术当作上下文喂给模型。
        """
        if not session_id or max_rounds <= 0:
            return []
        from app.models.qa_record import QARecord
        result = await db_session.execute(
            select(QARecord)
            .where(QARecord.session_id == session_id, QARecord.user_id == user_id)
            .order_by(desc(QARecord.created_at))
            .limit(max_rounds)
        )
        records = list(result.scalars().all())
        records.reverse()  # 时间正序
        messages = []
        for r in records:
            if not r.question or not r.answer:
                continue
            if r.answer.startswith("🔒"):  # 跳过权限拒绝话术
                continue
            messages.append({"role": "user", "content": r.question})
            messages.append({"role": "assistant", "content": r.answer})
        return messages

    @staticmethod
    def _preprocess(text: str) -> str:
        text = text.strip()
        text = re.sub(r"[？?！!。，,、\s]+", " ", text)
        return text


def build_response(ctx: QAContext) -> dict:
    """根据QA上下文构建API响应"""
    base = {
        "question": ctx.question,
        "answer": ctx.answer,
        "answer_type": ctx.answer_type.value if isinstance(ctx.answer_type, AnswerType) else ctx.answer_type,
        "reference_docs": ctx.reference_docs,
        "confidence": ctx.confidence,
        "session_id": ctx.session_id,
    }
    if ctx.filtered_doc_ids and ctx.answer_type not in [AnswerType.NO_RESULT]:
        base["notice"] = "🔒 部分相关制度需要HR权限才能查看，如需了解请联系HR部门"
    if ctx.personal_data_denied:
        base["notice"] = f"🔒 以下字段因权限不足未展示: {', '.join(ctx.personal_data_denied)}"
    if ctx.confidence and ctx.confidence < QA_THRESHOLDS.get("rag_low_confidence", 0.7):
        base["disclaimer"] = "以下回答仅供参考，建议与HR确认"
    return base


# 全局编排器实例（phase2 含完整RAG链）
qa_orchestrator = QAOrchestrator(phase="phase2")
