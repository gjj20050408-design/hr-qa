"""会话表 ChatSession — 存储会话标题和置顶状态"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import uuid4_str


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    session_id = Column(String(64), primary_key=True, default=uuid4_str)
    user_id = Column(String(64), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=True)  # 会话标题（默认取首条问题，可重命名）
    is_pinned = Column(Boolean, default=False)  # 是否置顶
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<ChatSession {self.session_id} {self.title}>"
