"""分类标签表 Category"""
from sqlalchemy import Column, String, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import uuid4_str
from app.enums.enums import CategoryType, AccessLevel


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(String(64), primary_key=True, default=uuid4_str)
    name = Column(String(100), nullable=False)
    parent_id = Column(String(64), ForeignKey("categories.category_id", ondelete="SET NULL"), nullable=True)
    type = Column(Enum(CategoryType, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    access_level = Column(Enum(AccessLevel, values_callable=lambda obj: [e.value for e in obj]), nullable=False, default=AccessLevel.ALL_ROLES)
    sort_order = Column(Integer, default=0)

    # 关系
    parent = relationship("Category", remote_side="Category.category_id", backref="children")
    documents = relationship("Document", back_populates="category")
    faqs = relationship("FAQ", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name} ({self.type.value})>"
