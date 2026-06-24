"""部门表 Department"""
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import uuid4_str


class Department(Base):
    __tablename__ = "departments"

    department_id = Column(String(64), primary_key=True, default=uuid4_str)
    name = Column(String(100), nullable=False)
    parent_id = Column(String(64), ForeignKey("departments.department_id", ondelete="SET NULL"), nullable=True)
    sort_order = Column(Integer, default=0)

    # 关系
    parent = relationship("Department", remote_side="Department.department_id", backref="children")
    users = relationship("User", back_populates="department")

    def __repr__(self):
        return f"<Department {self.name}>"
