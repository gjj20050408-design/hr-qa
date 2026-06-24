"""纠错与公告相关 Schema"""
from typing import Optional, List
from pydantic import BaseModel, Field


class CorrectionCreateRequest(BaseModel):
    """创建纠错申请请求"""
    document_id: str = Field(..., description="关联文档ID")
    section: str = Field(..., max_length=500, description="问题段落定位")
    description: str = Field(..., min_length=1, description="纠错说明")


class CorrectionReviewRequest(BaseModel):
    """审核纠错请求"""
    action: str = Field(..., description="审核动作: approved/rejected")
    comment: Optional[str] = Field(None, max_length=500, description="审核意见")


class AnnouncementCreateRequest(BaseModel):
    """创建公告请求"""
    title: str = Field(..., min_length=1, max_length=200, description="公告标题")
    content: str = Field(..., min_length=1, description="公告内容")
    priority: str = Field(default="normal", description="优先级: normal/important/urgent")
    target_type: str = Field(default="all", description="推送范围类型: all/department/role")
    target_ids: Optional[List[str]] = Field(None, description="目标范围ID列表")
    attachment: Optional[str] = Field(None, max_length=500, description="附件路径")
