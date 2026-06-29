"""问答记录表 QARecord"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, Float, Boolean, Enum, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import uuid4_str
from app.enums.enums import AnswerType, FeedbackType


class QARecord(Base):
    __tablename__ = "qa_records"

    record_id = Column(String(64), primary_key=True, default=uuid4_str)
    user_id = Column(String(64), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String(64), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    answer_type = Column(Enum(AnswerType, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    confidence = Column(Float, nullable=True)
    reference_docs = Column(JSON, nullable=True)
    response_time_ms = Column(Integer, default=0)
    feedback = Column(Enum(FeedbackType, values_callable=lambda obj: [e.value for e in obj]), nullable=True)
    feedback_reason = Column(String(500), nullable=True)
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<QARecord {self.record_id} [{self.answer_type.value}]>"
