"""个性化权益报告缓存表 BenefitReport

按 (user_id, year) 缓存为员工生成的专属权益清单。
权益数值由后端规则（RULE_TEMPLATES + 工龄）确定，LLM 仅润色文案。
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import uuid4_str


class BenefitReport(Base):
    __tablename__ = "benefit_reports"
    __table_args__ = (
        UniqueConstraint("user_id", "year", name="uq_benefit_user_year"),
    )

    report_id = Column(String(64), primary_key=True, default=uuid4_str)
    user_id = Column(String(64), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    year = Column(Integer, nullable=False)
    tenure_years = Column(Integer, nullable=True)  # 生成时的工龄快照
    items = Column(JSON, nullable=True)            # 权益条目 list[{title,value,description,category,source_rule}]
    summary = Column(Text, nullable=True)          # LLM 润色后的整体说明/寄语
    model = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<BenefitReport {self.user_id} {self.year}>"
