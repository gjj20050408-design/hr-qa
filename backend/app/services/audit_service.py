"""审计日志服务"""
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog


class AuditService:

    @staticmethod
    async def get_logs(
        db_session: AsyncSession, page: int = 1, page_size: int = 50,
        user_id: str = None, action: str = None,
        resource_type: str = None, resource_id: str = None,
    ) -> tuple:
        from sqlalchemy import func
        conditions = []
        if user_id:
            conditions.append(AuditLog.user_id == user_id)
        if action:
            conditions.append(AuditLog.action == action)
        if resource_type:
            conditions.append(AuditLog.resource_type == resource_type)
        if resource_id:
            conditions.append(AuditLog.resource_id == resource_id)

        query = select(AuditLog)
        count_query = select(func.count(AuditLog.log_id))
        for c in conditions:
            query = query.where(c)
            count_query = count_query.where(c)

        result = await db_session.execute(count_query)
        total = result.scalar() or 0

        query = query.order_by(desc(AuditLog.created_at)).offset((page - 1) * page_size).limit(page_size)
        result = await db_session.execute(query)
        logs = result.scalars().all()

        return logs, total

    @staticmethod
    async def create_log(
        user_id: str, action: str, resource_type: str,
        resource_id: str = None, detail: dict = None,
        ip_address: str = None, user_agent: str = None,
        db_session: AsyncSession = None,
    ) -> AuditLog:
        from app.models.base import uuid4_str
        log = AuditLog(
            log_id=uuid4_str(),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            detail=detail or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db_session.add(log)
        return log
