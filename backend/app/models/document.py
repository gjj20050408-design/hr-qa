"""制度文档表 Document — 含权限解析逻辑"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import uuid4_str
from app.enums.enums import (
    DocFormat, DocStatus, DocAccessLevel, AccessLevel, EmbeddingStatus,
)
from app.enums.constants import PERMISSION_MATRIX, DOC_TO_ACCESS_MAP
from app.enums.enums import Role


class Document(Base):
    __tablename__ = "documents"

    document_id = Column(String(64), primary_key=True, default=uuid4_str)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category_id = Column(String(64), ForeignKey("categories.category_id"), nullable=False)
    format = Column(Enum(DocFormat), nullable=False)
    version = Column(String(10), nullable=False, default="1.0")
    version_note = Column(String(500), nullable=True)
    status = Column(Enum(DocStatus), nullable=False, default=DocStatus.DRAFT)
    access_level = Column(Enum(DocAccessLevel), nullable=False, default=DocAccessLevel.INHERIT)
    uploaded_by = Column(String(64), ForeignKey("users.user_id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    word_count = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    embedding_status = Column(String(20), default=EmbeddingStatus.PENDING.value)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    category = relationship("Category", back_populates="documents")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    def effective_access_level(self) -> AccessLevel:
        """解析有效访问级别，考虑继承链"""
        if self.access_level == DocAccessLevel.INHERIT:
            if self.category:
                return self.category.access_level
            return AccessLevel.ALL_ROLES
        return DOC_TO_ACCESS_MAP.get(self.access_level, AccessLevel.ALL_ROLES)

    def can_access(self, role: Role) -> bool:
        """检查给定角色是否可访问本文档"""
        if role == Role.ADMIN:
            return True
        effective = self.effective_access_level()
        return PERMISSION_MATRIX.get((effective, role), False)

    def is_overridden(self) -> bool:
        return self.access_level != DocAccessLevel.INHERIT

    def publish(self) -> None:
        if self.status == DocStatus.DRAFT:
            self.status = DocStatus.PUBLISHED
            self.published_at = datetime.utcnow()

    def archive(self) -> None:
        self.status = DocStatus.ARCHIVED

    def __repr__(self):
        return f"<Document {self.title} v{self.version}>"
