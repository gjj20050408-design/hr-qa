"""问答服务 — 管理 QARecord、会话、反馈"""
import json
from typing import Optional
from datetime import datetime
from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.qa_record import QARecord
from app.models.chat_session import ChatSession
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
        # 如果会话不存在，自动创建（标题默认为首条问题）
        existing = await db_session.get(ChatSession, session_id)
        if not existing:
            new_session = ChatSession(
                session_id=session_id,
                user_id=user_id,
                title=question[:50] if question else "新对话",
            )
            db_session.add(new_session)

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
        """获取用户的会话列表（置顶优先，再按更新时间倒序）"""
        result = await db_session.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(desc(ChatSession.is_pinned), desc(ChatSession.created_at))
            .limit(50)
        )
        sessions = result.scalars().all()
        return [
            {
                "session_id": s.session_id,
                "title": s.title or "新对话",
                "created_at": str(s.created_at) if s.created_at else "",
                "updated_at": str(s.updated_at) if s.updated_at else "",
                "is_pinned": s.is_pinned,
            }
            for s in sessions
        ]

    @staticmethod
    async def rename_session(session_id: str, user_id: str, title: str, db_session: AsyncSession) -> ChatSession:
        session = await db_session.get(ChatSession, session_id)
        if not session:
            raise ValueError("会话不存在")
        if session.user_id != user_id:
            raise ValueError("无权操作此会话")
        session.title = title.strip()[:200] if title.strip() else "新对话"
        await db_session.flush()
        return session

    @staticmethod
    async def toggle_pin_session(session_id: str, user_id: str, db_session: AsyncSession) -> ChatSession:
        session = await db_session.get(ChatSession, session_id)
        if not session:
            raise ValueError("会话不存在")
        if session.user_id != user_id:
            raise ValueError("无权操作此会话")
        session.is_pinned = not session.is_pinned
        await db_session.flush()
        return session

    @staticmethod
    async def delete_session(session_id: str, user_id: str, db_session: AsyncSession) -> None:
        session = await db_session.get(ChatSession, session_id)
        if not session:
            return
        if session.user_id != user_id:
            raise ValueError("无权操作此会话")
        # 删除关联的问答记录
        records = await db_session.execute(
            select(QARecord).where(QARecord.session_id == session_id)
        )
        for r in records.scalars().all():
            await db_session.delete(r)
        await db_session.delete(session)
        await db_session.flush()
