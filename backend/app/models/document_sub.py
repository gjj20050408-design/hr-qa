"""文档相关子表 — DocumentVersion, DocumentChunk"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import uuid4_str


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    version_id = Column(String(64), primary_key=True, default=uuid4_str)
    document_id = Column(String(64), ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False)
    version = Column(String(10), nullable=False)
    content_snapshot = Column(Text, nullable=False)
    change_summary = Column(String(1000), nullable=True)
    changed_by = Column(String(64), ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="versions")
    changer = relationship("User", foreign_keys=[changed_by])

    def __repr__(self):
        return f"<DocumentVersion {self.document_id} v{self.version}>"


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    chunk_id = Column(String(64), primary_key=True, default=uuid4_str)
    document_id = Column(String(64), ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    embedding_status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")

    def __repr__(self):
        return f"<DocumentChunk {self.document_id}[{self.chunk_index}]>"
