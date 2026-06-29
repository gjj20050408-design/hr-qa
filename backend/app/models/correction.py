"""纠错申请表 CorrectionRequest"""
from datetime import datetime
from sqlalchemy import Column, String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import uuid4_str
from app.enums.enums import CorrectionStatus


class CorrectionRequest(Base):
    __tablename__ = "correction_requests"

    request_id = Column(String(64), primary_key=True, default=uuid4_str)
    document_id = Column(String(64), ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False)
    section = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    submitted_by = Column(String(64), ForeignKey("users.user_id"), nullable=False)
    reviewed_by = Column(String(64), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(CorrectionStatus, values_callable=lambda obj: [e.value for e in obj]), nullable=False, default=CorrectionStatus.PENDING)
    review_comment = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)

    document = relationship("Document", foreign_keys=[document_id])
    submitter = relationship("User", foreign_keys=[submitted_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])

    def __repr__(self):
        return f"<CorrectionRequest {self.request_id} [{self.status.value}]>"
