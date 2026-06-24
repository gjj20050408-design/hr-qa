"""分类管理相关 Schema"""
from typing import Optional, List
from pydantic import BaseModel, Field


class CategoryCreateRequest(BaseModel):
    """创建分类请求"""
    name: str = Field(..., min_length=1, max_length=100, description="分类名称")
    parent_id: Optional[str] = Field(None, description="上级分类ID")
    type: str = Field(..., description="分类类型: document/faq")
    access_level: str = Field(default="all_roles", description="默认检索权限级别")
    sort_order: int = Field(default=0)


class CategoryAccessUpdateRequest(BaseModel):
    """更新分类权限请求"""
    access_level: str = Field(..., description="检索权限级别")
    cascade: bool = Field(default=False, description="是否级联更新子文档权限")


class CategoryResponse(BaseModel):
    """分类响应"""
    category_id: str
    name: str
    parent_id: Optional[str] = None
    type: str
    access_level: str
    sort_order: int = 0
    children: Optional[List["CategoryResponse"]] = None
