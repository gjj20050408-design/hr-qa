"""问答服务 — 管理 QARecord、会话、反馈"""
import json
from typing import Optional
from datetime import datetime
from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.qa_record import QARecord
from app.models.base import uuid4_str
from app.enums.enums import AnswerType, FeedbackType


class QAService:

    @staticmethod
    async def save_record(
        user_id: str, session_id: str, question: str, answer: str,
        answer_type: str, confidence: float = None,
        reference_docs: list = None, response_time_ms: int = 0,
        db_session: AsyncSession = None,
    ) -> QARecord:
        record = QARecord(
            record_id=uuid4_str(),
            user_id=user_id,
            session_id=session_id,
            question=question,
            answer=answer,
            answer_type=AnswerType(answer_type) if answer_type in [a.value for a in AnswerType] else AnswerType.NO_RESULT,
            confidence=confidence,
            reference_docs=reference_docs if reference_docs else [],
            response_time_ms=response_time_ms,
        )
        db_session.add(record)
        await db_session.flush()
        return record

    @staticmethod
    async def get_user_records(
        user_id: str, db_session: AsyncSession,
        page: int = 1, page_size: int = 20,
        session_id: str = None, answer_type: str = None,
    ) -> tuple:
        conditions = [QARecord.user_id == user_id]
        if session_id:
            conditions.append(QARecord.session_id == session_id)
        if answer_type and answer_type in [a.value for a in AnswerType]:
            conditions.append(QARecord.answer_type == AnswerType(answer_type))

        count_query = select(func.count(QARecord.record_id)).where(*conditions)
        result = await db_session.execute(count_query)
        total = result.scalar() or 0

        query = (
            select(QARecord)
            .where(*conditions)
            .order_by(desc(QARecord.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db_session.execute(query)
        records = result.scalars().all()

        return records, total

    @staticmethod
    async def toggle_favorite(record_id: str, user_id: str, is_favorite: bool, db_session: AsyncSession) -> QARecord:
        record = await db_session.get(QARecord, record_id)
        if not record:
            raise ValueError("记录不存在")
        if record.user_id != user_id:
            raise ValueError("无权操作此记录")
        record.is_favorite = is_favorite
        await db_session.flush()
        return record

    @staticmethod
    async def submit_feedback(
        record_id: str, user_id: str, feedback: str, reason: str = None, db_session: AsyncSession = None,
    ) -> QARecord:
        record = await db_session.get(QARecord, record_id)
        if not record:
            raise ValueError("记录不存在")
        if record.user_id != user_id:
            raise ValueError("无权操作此记录")
        if feedback not in [f.value for f in FeedbackType]:
            raise ValueError("无效的反馈类型")
        record.feedback = FeedbackType(feedback)
        record.feedback_reason = reason
        await db_session.flush()
        return record

    @staticmethod
    async def get_user_stats(user_id: str, db_session: AsyncSession) -> dict:
        # 总提问数
        result = await db_session.execute(
            select(func.count(QARecord.record_id)).where(QARecord.user_id == user_id)
        )
        total_questions = result.scalar() or 0

        # 收藏数
        result = await db_session.execute(
            select(func.count(QARecord.record_id)).where(
                and_(QARecord.user_id == user_id, QARecord.is_favorite == True)
            )
        )
        favorites = result.scalar() or 0

        # 各类型回答数
        result = await db_session.execute(
            select(QARecord.answer_type, func.count(QARecord.record_id))
            .where(QARecord.user_id == user_id)
            .group_by(QARecord.answer_type)
        )
        type_distribution = {row[0].value: row[1] for row in result.all()}

        # 反馈统计
        result = await db_session.execute(
            select(
                func.count(QARecord.record_id).filter(QARecord.feedback == FeedbackType.HELPFUL),
                func.count(QARecord.record_id).filter(QARecord.feedback == FeedbackType.NOT_HELPFUL),
            ).where(QARecord.user_id == user_id)
        )
        stats = result.one_or_none()
        helpful = stats[0] if stats else 0
        not_helpful = stats[1] if stats else 0

        return {
            "total_questions": total_questions,
            "favorites": favorites,
            "answer_type_distribution": type_distribution,
            "helpful_count": helpful,
            "not_helpful_count": not_helpful,
        }

    @staticmethod
    async def get_sessions(user_id: str, db_session: AsyncSession) -> list:
        result = await db_session.execute(
            select(QARecord.session_id, func.min(QARecord.created_at), func.count(QARecord.record_id))
            .where(QARecord.user_id == user_id)
            .group_by(QARecord.session_id)
            .order_by(desc(func.min(QARecord.created_at)))
            .limit(20)
        )
        rows = result.all()
        return [{"session_id": r[0], "started_at": str(r[1]), "message_count": r[2]} for r in rows]
