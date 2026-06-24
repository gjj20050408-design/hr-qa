"""管理后台接口路由 — 纠错、公告、数据分析、审计日志"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_hr_plus, require_admin
from app.schemas.response import success_response, error_response, list_response
from app.schemas.correction import (
    CorrectionCreateRequest, CorrectionReviewRequest,
    AnnouncementCreateRequest,
)
from app.services.analytics_service import AnalyticsService
from app.services.audit_service import AuditService
from app.models.correction import CorrectionRequest
from app.models.announcement import Announcement, AnnouncementRead
from app.models.base import uuid4_str
from app.enums.enums import CorrectionStatus, Priority, TargetType
from sqlalchemy import select, func, desc

router = APIRouter(tags=["管理后台"])


# ── 纠错申请 ──

@router.post("/corrections")
async def create_correction(
    req: CorrectionCreateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """提交纠错申请"""
    cr = CorrectionRequest(
        request_id=uuid4_str(),
        document_id=req.document_id,
        section=req.section,
        description=req.description,
        submitted_by=current_user.user_id,
        status=CorrectionStatus.PENDING,
    )
    db.add(cr)
    await db.flush()
    return success_response(data={"request_id": cr.request_id}, message="纠错申请已提交")


@router.get("/corrections")
async def list_corrections(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """纠错申请列表"""
    conditions = []
    if status and status in [s.value for s in CorrectionStatus]:
        conditions.append(CorrectionRequest.status == CorrectionStatus(status))

    query = select(CorrectionRequest)
    count_query = select(func.count(CorrectionRequest.request_id))
    for c in conditions:
        query = query.where(c)
        count_query = count_query.where(c)

    result = await db.execute(count_query)
    total = result.scalar() or 0

    query = query.order_by(desc(CorrectionRequest.created_at)).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    crs = result.scalars().all()

    items = [
        {
            "request_id": r.request_id,
            "document_id": r.document_id,
            "section": r.section,
            "description": r.description,
            "submitted_by": r.submitted_by,
            "submitter_name": r.submitter.name if r.submitter else None,
            "status": r.status.value,
            "review_comment": r.review_comment,
            "created_at": str(r.created_at) if r.created_at else None,
            "reviewed_at": str(r.reviewed_at) if r.reviewed_at else None,
        }
        for r in crs
    ]
    return list_response(items=items, page=page, page_size=page_size, total=total)


@router.post("/corrections/{request_id}/review")
async def review_correction(
    request_id: str,
    req: CorrectionReviewRequest,
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """审核纠错申请"""
    from datetime import datetime
    cr = await db.get(CorrectionRequest, request_id)
    if not cr:
        raise HTTPException(status_code=404, detail=error_response(50002, "纠错申请不存在"))
    if cr.status != CorrectionStatus.PENDING:
        raise HTTPException(status_code=409, detail=error_response(50003, "该纠错已处理"))

    if req.action not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail=error_response(90001, "无效的审核动作"))

    cr.status = CorrectionStatus.APPROVED if req.action == "approved" else CorrectionStatus.REJECTED
    cr.reviewed_by = current_user.user_id
    cr.review_comment = req.comment
    cr.reviewed_at = datetime.utcnow()
    await db.flush()
    return success_response(data={"request_id": cr.request_id, "status": cr.status.value}, message="审核完成")


# ── 公告管理 ──

@router.post("/announcements")
async def create_announcement(
    req: AnnouncementCreateRequest,
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """发布公告"""
    ann = Announcement(
        announcement_id=uuid4_str(),
        title=req.title,
        content=req.content,
        priority=Priority(req.priority) if req.priority in [p.value for p in Priority] else Priority.NORMAL,
        target_type=TargetType(req.target_type) if req.target_type in [t.value for t in TargetType] else TargetType.ALL,
        target_ids=req.target_ids,
        attachment=req.attachment,
        published_by=current_user.user_id,
    )
    db.add(ann)
    await db.flush()
    return success_response(data={"announcement_id": ann.announcement_id, "title": ann.title}, message="公告发布成功")


@router.get("/announcements")
async def list_announcements(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """公告列表"""
    query = select(Announcement).order_by(desc(Announcement.published_at))
    count_query = select(func.count(Announcement.announcement_id))

    result = await db.execute(count_query)
    total = result.scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    anns = result.scalars().all()

    items = [
        {
            "announcement_id": a.announcement_id,
            "title": a.title,
            "content": a.content,
            "priority": a.priority.value,
            "target_type": a.target_type.value,
            "published_by": a.published_by,
            "publisher_name": a.publisher.name if a.publisher else None,
            "published_at": str(a.published_at) if a.published_at else None,
            "attachment": a.attachment,
        }
        for a in anns
    ]
    return list_response(items=items, page=page, page_size=page_size, total=total)


@router.get("/announcements/{announcement_id}/reads")
async def get_announcement_reads(
    announcement_id: str,
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """公告阅读状态"""
    result = await db.execute(
        select(AnnouncementRead).where(AnnouncementRead.announcement_id == announcement_id)
    )
    reads = result.scalars().all()
    items = [
        {
            "read_id": r.read_id,
            "user_id": r.user_id,
            "is_read": r.is_read,
            "read_at": str(r.read_at) if r.read_at else None,
            "remind_count": r.remind_count,
        }
        for r in reads
    ]
    return success_response(data={"items": items})


# ── 数据分析 ──

@router.get("/analytics/dashboard")
async def get_dashboard(
    time_range: str = Query("7d"),
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """数据驾驶舱"""
    stats = await AnalyticsService.get_dashboard_stats(
        db_session=db, time_range=time_range,
    )
    return success_response(data=stats)


# ── 审计日志 ──

@router.get("/audit/logs")
async def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """查询审计日志（仅管理员）"""
    logs, total = await AuditService.get_logs(
        db_session=db, page=page, page_size=page_size,
        user_id=user_id, action=action,
        resource_type=resource_type, resource_id=resource_id,
    )
    items = [
        {
            "log_id": l.log_id,
            "user_id": l.user_id,
            "action": l.action,
            "resource_type": l.resource_type,
            "resource_id": l.resource_id,
            "detail": l.detail,
            "ip_address": l.ip_address,
            "user_agent": l.user_agent,
            "created_at": str(l.created_at) if l.created_at else None,
        }
        for l in logs
    ]
    return list_response(items=items, page=page, page_size=page_size, total=total)
