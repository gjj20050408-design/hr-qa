"""数据统计相关 Schema"""
from typing import Optional
from pydantic import BaseModel, Field


class AnalyticsQueryRequest(BaseModel):
    """统计查询请求"""
    time_range: Optional[str] = Field(default="7d", description="时间范围: 7d/30d/90d/1y")
    category_id: Optional[str] = Field(None, description="分类ID筛选")


class DashboardStatsResponse(BaseModel):
    """仪表盘统计响应"""
    total_questions: int = 0
    today_questions: int = 0
    faq_match_rate: float = 0.0
    avg_response_time_ms: float = 0.0
    answer_type_distribution: Optional[dict] = None
    daily_trend: Optional[list] = None
    hot_topics: Optional[list] = None
    category_distribution: Optional[list] = None
