"""制度解读服务 — 用 LLM 将制度条文转成通俗图文 / 流程图 / 对比表格

按需实时生成 + 按 (document_id, doc_version) 缓存。
权限门禁复用 Document.can_access。
"""
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.enums import Role
from app.models.interpretation import PolicyInterpretation
from app.services.document_service import DocumentService
from app.utils.llm_json import parse_llm_json

logger = logging.getLogger(__name__)


class PermissionDeniedError(Exception):
    """无权访问该文档"""


class InterpretationService:

    SYSTEM_PROMPT = (
        "你是企业HR制度解读助手。请把给定的制度文档转写成通俗易懂的解读，"
        "帮助普通员工快速理解。严格只依据提供的文档内容，不要编造制度中没有的规定。\n\n"
        "请输出 JSON（不要输出任何其他内容），格式如下：\n"
        "{\n"
        '  "summary": "用通俗语言概括这份制度的核心内容，可用 markdown，3-6 句",\n'
        '  "flowchart": "若制度包含办理/审批流程，用 mermaid flowchart TD 语法描述；无流程则为空字符串",\n'
        '  "comparison_table": "若制度包含分档/分类规则（如不同工龄对应不同待遇），用 markdown 表格呈现；无则为空字符串",\n'
        '  "key_points": ["要点1", "要点2", "要点3"]\n'
        "}\n\n"
        "约束：\n"
        "1. flowchart 必须是合法的 mermaid flowchart TD 语法，节点文字用中文，避免特殊符号\n"
        "2. comparison_table 必须是标准 markdown 表格\n"
        "3. key_points 为 3-6 条最关键的提示\n"
        "4. 全部使用中文"
    )

    @staticmethod
    async def get_or_generate(
        document_id: str, user_role: Role, db_session: AsyncSession,
        force: bool = False,
    ) -> dict:
        """获取或生成制度解读。

        force=True 时忽略并覆盖缓存（重新生成）。
        无权访问抛 PermissionDeniedError；文档不存在抛 ValueError。
        """
        doc = await DocumentService.get_document_detail(document_id, db_session)
        if not doc.can_access(user_role):
            raise PermissionDeniedError("无权查看该制度文档")

        version = doc.version or "1.0"

        # 缓存命中
        if not force:
            cached = await InterpretationService._get_cache(document_id, version, db_session)
            if cached:
                return InterpretationService._to_dict(cached, doc, cached_hit=True)

        # 生成
        generated = InterpretationService._generate(doc)
        if generated is None:
            # LLM 不可用 → 降级，不写缓存
            return {
                "document_id": document_id,
                "title": doc.title,
                "doc_version": version,
                "summary": (doc.content or "")[:500],
                "flowchart": "",
                "comparison_table": "",
                "key_points": [],
                "degraded": True,
                "message": "AI 解读服务暂不可用，已展示制度原文摘要",
            }

        # 写缓存（force 时先删旧）
        if force:
            await InterpretationService._delete_cache(document_id, version, db_session)
        record = PolicyInterpretation(
            document_id=document_id,
            doc_version=version,
            summary=generated.get("summary", ""),
            flowchart=generated.get("flowchart", ""),
            comparison_table=generated.get("comparison_table", ""),
            key_points=generated.get("key_points", []),
            model=generated.get("_model", ""),
        )
        db_session.add(record)
        await db_session.flush()
        return InterpretationService._to_dict(record, doc, cached_hit=False)

    @staticmethod
    async def _get_cache(document_id: str, version: str, db_session: AsyncSession) -> Optional[PolicyInterpretation]:
        result = await db_session.execute(
            select(PolicyInterpretation).where(
                PolicyInterpretation.document_id == document_id,
                PolicyInterpretation.doc_version == version,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def _delete_cache(document_id: str, version: str, db_session: AsyncSession) -> None:
        existing = await InterpretationService._get_cache(document_id, version, db_session)
        if existing:
            await db_session.delete(existing)
            await db_session.flush()

    @staticmethod
    def _generate(doc) -> Optional[dict]:
        """调用 LLM 生成结构化解读，失败/不可用返回 None"""
        from app.providers.llm import llm_provider

        if isinstance(llm_provider, type(None)):
            return None
        try:
            if not llm_provider.health_check():
                logger.info("InterpretationService: LLM unavailable, degrade")
                return None
        except Exception:
            return None

        content_text = (doc.content or "")[:6000]
        prompt = (
            f"制度文档标题：{doc.title}\n\n"
            f"制度文档内容：\n{content_text}\n\n"
            "请按系统要求输出 JSON 解读。"
        )
        try:
            resp = llm_provider.generate(
                prompt=prompt,
                system_prompt=InterpretationService.SYSTEM_PROMPT,
                max_tokens=2048,
                temperature=0,
            )
            if not resp.content or resp.content.startswith("[LLM"):
                return None
            data = parse_llm_json(resp.content)
            if data is None:
                logger.warning(f"InterpretationService: parse failed: {resp.content[:200]}")
                return None
            # 标准化
            data.setdefault("summary", "")
            data.setdefault("flowchart", "")
            data.setdefault("comparison_table", "")
            kp = data.get("key_points", [])
            data["key_points"] = kp if isinstance(kp, list) else []
            data["_model"] = resp.model
            return data
        except Exception as e:
            logger.error(f"InterpretationService: generate failed: {e}")
            return None

    @staticmethod
    def _to_dict(record: PolicyInterpretation, doc, cached_hit: bool) -> dict:
        return {
            "document_id": record.document_id,
            "title": doc.title,
            "doc_version": record.doc_version,
            "summary": record.summary or "",
            "flowchart": record.flowchart or "",
            "comparison_table": record.comparison_table or "",
            "key_points": record.key_points or [],
            "model": record.model or "",
            "created_at": str(record.created_at) if record.created_at else None,
            "cached": cached_hit,
            "degraded": False,
        }
