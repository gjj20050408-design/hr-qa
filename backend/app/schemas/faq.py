"""FAQ 管理相关 Schema"""
from typing import Optional
from pydantic import BaseModel, Field


class FAQCreateRequest(BaseModel):
    """创建 FAQ 请求"""
    question: str = Field(..., min_length=1, max_length=500, description="问题")
    answer: str = Field(..., min_length=1, description="标准答案")
    category_id: str = Field(..., description="FAQ分类ID")
    related_doc_id: Optional[str] = Field(None, description="关联制度文档ID")
    keywords: Optional[str] = Field(None, max_length=500, description="关键词(逗号分隔)")


class FAQUpdateRequest(BaseModel):
    """更新 FAQ 请求"""
    question: Optional[str] = Field(None, max_length=500)
    answer: Optional[str] = None
    category_id: Optional[str] = None
    related_doc_id: Optional[str] = None
    keywords: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = None


class FAQResponse(BaseModel):
    """FAQ 响应"""
    faq_id: str
    question: str
    answer: str
    category_id: str
    category_name: Optional[str] = None
    related_doc_id: Optional[str] = None
    keywords: Optional[str] = None
    view_count: int = 0
    status: str
    created_by: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
