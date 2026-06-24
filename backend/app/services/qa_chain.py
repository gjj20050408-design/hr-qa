"""问答策略链 — 责任链模式实现

一期策略链: FAQ匹配 → 规则匹配 → 权限过滤 → 全文搜索 → 兜底
二期预留: RAG 处理器 + 个人数据守卫
"""
import re
import json
import copy
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import jieba
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.enums import Role, AnswerType, FAQStatus, DocStatus, AccessLevel
from app.enums.constants import (
    RULE_TEMPLATES, QA_THRESHOLDS, DEFAULT_USER_CONTEXT,
    PERMISSION_MATRIX, DOC_TO_ACCESS_MAP,
)
from app.models.faq import FAQ
from app.models.document import Document


@dataclass
class QAContext:
    """策略链中传递的上下文对象"""
    question: str
    processed_question: str = ""
    user_id: str = ""
    user_role: Role = Role.EMPLOYEE
    user_context: dict = field(default_factory=dict)
    session_id: str = ""
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
                func.match(FAQ.question, FAQ.keywords).against(keywords),
            ).limit(5)
        )
        faqs = result.scalars().all()

        best, best_score = None, 0.0
        for faq in faqs:
            score = self._similarity(ctx.processed_question, faq.question)
            if score > best_score:
                best_score = score
                best = faq

        if best and best_score >= QA_THRESHOLDS["faq_similarity_min"]:
            best.view_count += 1
            ctx.answer = best.answer
            ctx.answer_type = AnswerType.FAQ
            ctx.reference_docs = [{"doc_id": best.related_doc_id, "title": "FAQ标准答案"}]
            ctx.confidence = best_score
            ctx.is_done = True
        return await self.handle_next(ctx, db_session)

    @staticmethod
    def _similarity(q1: str, q2: str) -> float:
        def bigrams(s):
            return set(s[i:i+2] for i in range(len(s)-1))
        b1, b2 = bigrams(q1), bigrams(q2)
        if not b1 or not b2:
            return 0.0
        return len(b1 & b2) / len(b1 | b2)


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
            years = datetime.utcnow().date().year - hire.year
            result = result.replace("{tenure_years}", str(years))
        if "{annual_leave_days}" in result and uctx.get("hire_date"):
            hire = uctx["hire_date"]
            if isinstance(hire, str):
                hire = datetime.strptime(hire, "%Y-%m-%d").date() if "-" in str(hire) else datetime.strptime(str(hire), "%Y-%m-%d").date()
            years = datetime.utcnow().date().year - hire.year
            days = 5 if years < 3 else (10 if years < 10 else 15)
            result = result.replace("{annual_leave_days}", str(days))
        return result


class PermissionFilter(QAHandler):
    """④ 权限过滤处理器 — 横切关注点，注解上下文"""

    async def handle(self, ctx: QAContext, db_session: AsyncSession) -> QAContext:
        return await self.handle_next(ctx, db_session)

    @staticmethod
    def filter_documents(docs: list, role: Role) -> tuple:
        allowed, filtered = [], []
        for doc in docs:
            if doc.can_access(role):
                allowed.append(doc)
            else:
                filtered.append(doc)
        return allowed, filtered


class SearchHandler(QAHandler):
    """⑤ 全文搜索处理器"""

    async def handle(self, ctx: QAContext, db_session: AsyncSession) -> QAContext:
        result = await db_session.execute(
            select(Document).where(
                Document.status == DocStatus.PUBLISHED,
                func.match(Document.title, Document.content).against(ctx.processed_question),
            ).limit(QA_THRESHOLDS["search_max_results"])
        )
        docs = result.scalars().all()

        allowed, filtered = PermissionFilter.filter_documents(docs, ctx.user_role)
        ctx.filtered_doc_ids = [d.document_id for d in filtered]

        if allowed:
            snippets = []
            for doc in allowed:
                snippet = self._generate_snippet(doc.content, ctx.processed_question)
                snippets.append({
                    "document_id": doc.document_id,
                    "title": doc.title,
                    "snippet": snippet,
                    "category": doc.category.name if doc.category else "",
                    "version": doc.version,
                })
            ctx.answer = json.dumps(snippets, ensure_ascii=False)
            ctx.answer_type = AnswerType.SEARCH
            ctx.reference_docs = [{"doc_id": s["document_id"], "title": s["title"]} for s in snippets]
            ctx.is_done = True
        return await self.handle_next(ctx, db_session)

    @staticmethod
    def _generate_snippet(content: str, query: str) -> str:
        idx = content.find(query)
        if idx == -1:
            for ch in query:
                idx = content.find(ch)
                if idx != -1:
                    break
        if idx == -1:
            return content[:150] + "..."
        start = max(0, idx - 50)
        end = min(len(content), idx + 100)
        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet += "..."
        return snippet


class FallbackHandler(QAHandler):
    """⑦ 最终兜底处理器"""

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
    """问答编排器 — 构建并执行策略链"""

    def __init__(self, phase: str = "phase1"):
        self.phase = phase
        self._chain: Optional[QAHandler] = None

    def build_chain(self) -> QAHandler:
        faq = FAQMatcher()
        rule = RuleMatcher()
        perm_filter = PermissionFilter()
        search = SearchHandler()
        fallback = FallbackHandler()

        faq.set_next(rule)
        rule.set_next(perm_filter)
        perm_filter.set_next(search)
        search.set_next(fallback)

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
        )
        handler = self._chain or self.build_chain()
        return await handler.handle(ctx, db_session)

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
    if ctx.confidence and ctx.confidence < QA_THRESHOLDS.get("rag_low_confidence", 0.7):
        base["disclaimer"] = "以下回答仅供参考，建议与HR确认"
    return base


# 全局编排器实例
qa_orchestrator = QAOrchestrator(phase="phase1")
