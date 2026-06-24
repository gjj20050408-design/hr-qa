"""通知公告表 — Announcement, AnnouncementRead"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, Boolean, Enum, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import uuid4_str
from app.enums.enums import Priority, TargetType


class Announcement(Base):
    __tablename__ = "announcements"

    announcement_id = Column(String(64), primary_key=True, default=uuid4_str)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    priority = Column(Enum(Priority), nullable=False, default=Priority.NORMAL)
    target_type = Column(Enum(TargetType), nullable=False, default=TargetType.ALL)
    target_ids = Column(JSON, nullable=True)
    attachment = Column(String(500), nullable=True)
    published_by = Column(String(64), ForeignKey("users.user_id"), nullable=False)
    published_at = Column(DateTime, default=datetime.utcnow)

    publisher = relationship("User", foreign_keys=[published_by])
    reads = relationship("AnnouncementRead", back_populates="announcement", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Announcement {self.title}>"


class AnnouncementRead(Base):
    __tablename__ = "announcement_reads"

    read_id = Column(String(64), primary_key=True, default=uuid4_str)
    announcement_id = Column(String(64), ForeignKey("announcements.announcement_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(64), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    remind_count = Column(Integer, default=0)

    announcement = relationship("Announcement", back_populates="reads")
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<AnnouncementRead {self.announcement_id} by {self.user_id}>"
