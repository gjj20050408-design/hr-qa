"""FAQ 表"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import uuid4_str, CaseInsensitiveEnum
from app.enums.enums import FAQStatus


class FAQ(Base):
    __tablename__ = "faqs"

    faq_id = Column(String(64), primary_key=True, default=uuid4_str)
    question = Column(String(500), nullable=False)
    answer = Column(Text, nullable=False)
    category_id = Column(String(64), ForeignKey("categories.category_id"), nullable=False)
    related_doc_id = Column(String(64), ForeignKey("documents.document_id", ondelete="SET NULL"), nullable=True)
    keywords = Column(String(500), nullable=True)
    view_count = Column(Integer, default=0)
    status = Column(CaseInsensitiveEnum(FAQStatus), nullable=False, default=FAQStatus.ACTIVE)
    created_by = Column(String(64), ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="faqs")
    related_doc = relationship("Document", foreign_keys=[related_doc_id])
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<FAQ {self.question[:30]}...>"
