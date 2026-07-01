"""制度解读缓存表 PolicyInterpretation

按 (document_id, doc_version) 缓存 AI 生成的制度解读，文档版本变化即自然失效。
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import uuid4_str


class PolicyInterpretation(Base):
    __tablename__ = "policy_interpretations"
    __table_args__ = (
        UniqueConstraint("document_id", "doc_version", name="uq_interpretation_doc_version"),
    )

    interpretation_id = Column(String(64), primary_key=True, default=uuid4_str)
    document_id = Column(String(64), ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False)
    doc_version = Column(String(10), nullable=False, default="1.0")
    summary = Column(Text, nullable=True)          # 通俗摘要（markdown）
    flowchart = Column(Text, nullable=True)        # mermaid 流程图语法
    comparison_table = Column(Text, nullable=True) # markdown 对比表格
    key_points = Column(JSON, nullable=True)       # 要点列表 list[str]
    model = Column(String(50), nullable=True)      # 生成所用模型
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", foreign_keys=[document_id])

    def __repr__(self):
        return f"<PolicyInterpretation {self.document_id} v{self.doc_version}>"
