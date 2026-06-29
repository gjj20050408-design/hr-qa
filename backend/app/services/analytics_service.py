"""数据分析服务 — 仪表盘统计、热点分析"""
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.qa_record import QARecord
from app.models.faq import FAQ
from app.models.document import Document
from app.models.user import User
from app.models.category import Category
from app.models.correction import CorrectionRequest
from app.enums.enums import AnswerType, DocStatus, CorrectionStatus


class AnalyticsService:

    @staticmethod
    async def get_dashboard_stats(
        db_session: AsyncSession, time_range: str = "7d",
        category_id: str = None,
    ) -> dict:
        # 计算时间范围
        days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}.get(time_range, 7)
        since = datetime.now(timezone.utc) - timedelta(days=days)

        # ── 基础统计 ──

        # 总问题数
        result = await db_session.execute(
            select(func.count(QARecord.record_id))
        )
        total_questions = result.scalar() or 0

        # 今日问题数
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
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

        # ── 每日趋势（按时间范围过滤） ──
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

        # ── 热点话题（Top FAQ 匹配，按查看次数） ──
        result = await db_session.execute(
            select(FAQ.question, FAQ.view_count)
            .order_by(FAQ.view_count.desc())
            .limit(10)
        )
        hot_topics = [{"question": r[0], "view_count": r[1]} for r in result.all()]

        # ── 热门搜索词 TOP10（从问答记录的问题中提取关键词统计） ──
        result = await db_session.execute(
            select(QARecord.question, func.count(QARecord.record_id).label("cnt"))
            .where(QARecord.created_at >= since)
            .group_by(QARecord.question)
            .order_by(func.count(QARecord.record_id).desc())
            .limit(10)
        )
        hot_search_terms = [{"term": r[0], "count": r[1]} for r in result.all()]

        # ── 分类分布 ──
        result = await db_session.execute(
            select(Document.category_id, func.count(Document.document_id))
            .where(Document.status == DocStatus.PUBLISHED)
            .group_by(Document.category_id)
        )
        cat_dist = []
        for row in result.all():
            cat_dist.append({"category_id": row[0], "count": row[1]})

        # ── 文档与分类总数 ──
        result = await db_session.execute(
            select(func.count(Document.document_id))
            .where(Document.status == DocStatus.PUBLISHED)
        )
        total_documents = result.scalar() or 0

        result = await db_session.execute(
            select(func.count(Category.category_id))
        )
        total_categories = result.scalar() or 0

        # ── FAQ 总数 ──
        result = await db_session.execute(
            select(func.count(FAQ.faq_id))
        )
        total_faqs = result.scalar() or 0

        # ── 用户数 ──
        result = await db_session.execute(
            select(func.count(User.user_id))
        )
        total_users = result.scalar() or 0

        # ── 纠错统计 ──
        result = await db_session.execute(
            select(CorrectionRequest.status, func.count(CorrectionRequest.request_id))
            .group_by(CorrectionRequest.status)
        )
        corr_stats_raw = {row[0].value: row[1] for row in result.all()}
        correction_stats = {
            "total": sum(corr_stats_raw.values()),
            "pending": corr_stats_raw.get(CorrectionStatus.PENDING.value, 0),
            "approved": corr_stats_raw.get(CorrectionStatus.APPROVED.value, 0),
            "rejected": corr_stats_raw.get(CorrectionStatus.REJECTED.value, 0),
        }

        return {
            "total_questions": total_questions,
            "today_questions": today_questions,
            "faq_match_rate": round(faq_match_rate, 1),
            "avg_response_time_ms": round(avg_response, 0),
            "answer_type_distribution": type_dist,
            "daily_trend": daily_trend,
            "hot_topics": hot_topics,
            "hot_search_terms": hot_search_terms,
            "category_distribution": cat_dist,
            "total_documents": total_documents,
            "total_categories": total_categories,
            "total_faqs": total_faqs,
            "total_users": total_users,
            "correction_stats": correction_stats,
        }
