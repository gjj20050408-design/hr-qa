"""FAQ 管理服务"""
from typing import Optional
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.faq import FAQ
from app.models.audit_log import AuditLog
from app.models.base import uuid4_str
from app.enums.enums import FAQStatus


class FAQService:

    @staticmethod
    async def create_faq(
        question: str, answer: str, category_id: str, created_by: str,
        related_doc_id: str = None, keywords: str = None,
        db_session: AsyncSession = None,
    ) -> FAQ:
        faq = FAQ(
            faq_id=uuid4_str(),
            question=question,
            answer=answer,
            category_id=category_id,
            related_doc_id=related_doc_id,
            keywords=keywords,
            status=FAQStatus.ACTIVE,
            created_by=created_by,
        )
        db_session.add(faq)

        audit = AuditLog(
            log_id=uuid4_str(), user_id=created_by,
            action="faq_create", resource_type="faq",
            resource_id=faq.faq_id,
            detail={"question": question[:50]},
        )
        db_session.add(audit)
        await db_session.flush()
        return faq

    @staticmethod
    async def get_faqs(
        db_session: AsyncSession, page: int = 1, page_size: int = 20,
        category_id: str = None, status: str = None, keyword: str = None,
    ) -> tuple:
        conditions = []
        if category_id:
            conditions.append(FAQ.category_id == category_id)
        if status and status in [s.value for s in FAQStatus]:
            conditions.append(FAQ.status == FAQStatus(status))
        if keyword:
            conditions.append(FAQ.question.contains(keyword))

        query = select(FAQ)
        for c in conditions:
            query = query.where(c)

        count_query = select(func.count(FAQ.faq_id))
        for c in conditions:
            count_query = count_query.where(c)
        result = await db_session.execute(count_query)
        total = result.scalar() or 0

        query = query.order_by(desc(FAQ.updated_at)).offset((page - 1) * page_size).limit(page_size)
        result = await db_session.execute(query)
        faqs = result.scalars().all()

        return faqs, total

    @staticmethod
    async def update_faq(
        faq_id: str, db_session: AsyncSession, user_id: str,
        question: str = None, answer: str = None, category_id: str = None,
        related_doc_id: str = None, keywords: str = None, status: str = None,
    ) -> FAQ:
        faq = await db_session.get(FAQ, faq_id)
        if not faq:
            raise ValueError("FAQ不存在")

        if question is not None:
            faq.question = question
        if answer is not None:
            faq.answer = answer
        if category_id is not None:
            faq.category_id = category_id
        if related_doc_id is not None:
            faq.related_doc_id = related_doc_id
        if keywords is not None:
            faq.keywords = keywords
        if status is not None and status in [s.value for s in FAQStatus]:
            faq.status = FAQStatus(status)

        audit = AuditLog(
            log_id=uuid4_str(), user_id=user_id,
            action="faq_update", resource_type="faq",
            resource_id=faq.faq_id,
        )
        db_session.add(audit)
        await db_session.flush()
        return faq

    @staticmethod
    async def delete_faq(faq_id: str, user_id: str, db_session: AsyncSession) -> None:
        faq = await db_session.get(FAQ, faq_id)
        if not faq:
            raise ValueError("FAQ不存在")
        faq.status = FAQStatus.ARCHIVED

        audit = AuditLog(
            log_id=uuid4_str(), user_id=user_id,
            action="faq_archive", resource_type="faq",
            resource_id=faq_id,
        )
        db_session.add(audit)
        await db_session.flush()
