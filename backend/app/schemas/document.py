"""文档管理相关 Schema"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentCreateRequest(BaseModel):
    """创建/上传文档请求"""
    title: str = Field(..., min_length=1, max_length=200, description="文档标题")
    category_id: str = Field(..., description="分类ID")
    format: str = Field(..., description="文档格式: pdf/word/markdown/html")
    access_level: str = Field(default="inherit", description="检索权限级别")
    version_note: Optional[str] = Field(None, max_length=500, description="版本说明")


class DocumentUpdateRequest(BaseModel):
    """更新文档请求"""
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    category_id: Optional[str] = None
    access_level: Optional[str] = None
    version_note: Optional[str] = Field(None, max_length=500)


class DocumentAccessUpdateRequest(BaseModel):
    """更新文档权限请求"""
    access_level: str = Field(..., description="检索权限级别: inherit/all_roles/hr_admin_only/admin_only")


class DocumentResponse(BaseModel):
    """文档响应"""
    document_id: str
    title: str
    category_id: str
    category_name: Optional[str] = None
    format: str
    version: str
    version_note: Optional[str] = None
    status: str
    access_level: str
    uploaded_by: str
    uploader_name: Optional[str] = None
    word_count: int = 0
    chunk_count: int = 0
    embedding_status: str = "pending"
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DocumentVersionResponse(BaseModel):
    """文档版本历史响应"""
    version_id: str
    document_id: str
    version: str
    change_summary: Optional[str] = None
    changed_by: str
    changer_name: Optional[str] = None
    created_at: Optional[datetime] = None


class DocumentDiffRequest(BaseModel):
    """文档版本对比请求"""
    version_id_1: str
    version_id_2: str
