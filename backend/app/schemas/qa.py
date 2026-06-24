"""问答相关 Schema"""
from typing import Optional, List
from pydantic import BaseModel, Field


class AskQuestionRequest(BaseModel):
    """提交问题请求"""
    question: str = Field(..., min_length=1, max_length=1000, description="问题内容")
    session_id: Optional[str] = Field(None, description="会话ID（多轮对话）")


class AskQuestionResponse(BaseModel):
    """问答响应"""
    record_id: str
    question: str
    answer: str
    answer_type: str
    confidence: Optional[float] = None
    reference_docs: Optional[List[dict]] = None
    session_id: str
    response_time_ms: int = 0
    notice: Optional[str] = None
    disclaimer: Optional[str] = None


class FeedbackRequest(BaseModel):
    """答案反馈请求"""
    feedback: str = Field(..., description="反馈类型: helpful/not_helpful")
    reason: Optional[str] = Field(None, max_length=500, description="负面反馈原因")


class FavoriteToggleRequest(BaseModel):
    """收藏切换请求"""
    is_favorite: bool = Field(..., description="是否收藏")


class SessionCreateRequest(BaseModel):
    """创建会话请求"""
    pass  # 目前无需额外参数，由 JWT 自动识别用户


class SearchRequest(BaseModel):
    """搜索请求（Query 参数也可用）"""
    keyword: str = Field(..., min_length=1, max_length=100, description="搜索关键词")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
