"""数据分析服务 — 仪表盘统计、热点分析"""
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.qa_record import QARecord
from app.models.faq import FAQ
from app.models.document import Document
from app.models.user import User
from app.enums.enums import AnswerType, DocStatus


class AnalyticsService:

    @staticmethod
    async def get_dashboard_stats(
        db_session: AsyncSession, time_range: str = "7d",
        category_id: str = None,
    ) -> dict:
        # 计算时间范围
        days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}.get(time_range, 7)
        since = datetime.utcnow() - timedelta(days=days)

        # 总问题数
        result = await db_session.execute(
            select(func.count(QARecord.record_id))
        )
        total_questions = result.scalar() or 0

        # 今日问题数
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        result = await db_session.execute(
            select(func.count(QARecord.record_id)).where(QARecord.created_at >= today_start)
        )
        today_questions = result.scalar() or 0

        # 回答类型分布
        result = await db_session.execute(
            select(QARecord.answer_type, func.count(QARecord.record_id))
            .group_by(QARecord.answer_type)
        )
        type_dist = {row[0].value: row[1] for row in result.all()}

        # FAQ 匹配率
        faq_count = type_dist.get("faq", 0)
        total_period = sum(type_dist.values())
        faq_match_rate = (faq_count / total_period * 100) if total_period > 0 else 0.0

        # 平均响应时间
        result = await db_session.execute(
            select(func.avg(QARecord.response_time_ms))
        )
        avg_response = result.scalar() or 0.0

        # 每日趋势
        result = await db_session.execute(
            select(
                func.date(QARecord.created_at),
                func.count(QARecord.record_id),
            )
            .where(QARecord.created_at >= since)
            .group_by(func.date(QARecord.created_at))
            .order_by(func.date(QARecord.created_at))
        )
        daily_trend = [{"date": str(r[0]), "count": r[1]} for r in result.all()]

        # 热点话题（Top FAQ 匹配）
        result = await db_session.execute(
            select(FAQ.question, FAQ.view_count)
            .order_by(FAQ.view_count.desc())
            .limit(10)
        )
        hot_topics = [{"question": r[0], "view_count": r[1]} for r in result.all()]

        # 分类分布
        result = await db_session.execute(
            select(Document.category_id, func.count(Document.document_id))
            .where(Document.status == DocStatus.PUBLISHED)
            .group_by(Document.category_id)
        )
        cat_dist = []
        for row in result.all():
            cat_dist.append({"category_id": row[0], "count": row[1]})

        # 用户数
        result = await db_session.execute(
            select(func.count(User.user_id))
        )
        total_users = result.scalar() or 0

        return {
            "total_questions": total_questions,
            "today_questions": today_questions,
            "faq_match_rate": round(faq_match_rate, 1),
            "avg_response_time_ms": round(avg_response, 0),
            "answer_type_distribution": type_dist,
            "daily_trend": daily_trend,
            "hot_topics": hot_topics,
            "category_distribution": cat_dist,
            "total_users": total_users,
            "total_documents": 0,  # 可扩展
        }
