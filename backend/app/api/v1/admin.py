"""管理后台接口路由 — 纠错、公告、数据分析、审计日志、员工导入"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_hr_plus, require_admin
from app.schemas.response import success_response, error_response, list_response
from app.schemas.correction import (
    CorrectionCreateRequest, CorrectionReviewRequest,
    AnnouncementCreateRequest, AnnouncementMarkReadRequest,
)
from app.services.analytics_service import AnalyticsService
from app.services.audit_service import AuditService
from app.models.correction import CorrectionRequest
from app.models.announcement import Announcement, AnnouncementRead
from app.models.user import User
from app.models.base import uuid4_str
from app.enums.enums import CorrectionStatus, Priority, TargetType, UserStatus
from sqlalchemy import select, func, desc, or_

router = APIRouter(tags=["管理后台"])


# ── 纠错申请 ──

@router.post("/corrections")
async def create_correction(
    req: CorrectionCreateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """提交纠错申请"""
    # 验证文档是否存在
    from app.models.document import Document
    doc = await db.get(Document, req.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail=error_response(30001, "文档不存在"))

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
    from datetime import datetime, timezone
    cr = await db.get(CorrectionRequest, request_id)
    if not cr:
        raise HTTPException(status_code=404, detail=error_response(50002, "纠错申请不存在"))
    if cr.status != CorrectionStatus.PENDING:
        raise HTTPException(status_code=409, detail=error_response(50003, "该纠错已处理"))

    if req.action not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail=error_response(90001, "无效的审核动作"))

    # 驳回时必须填写审核意见
    if req.action == "rejected" and (not req.comment or not req.comment.strip()):
        raise HTTPException(status_code=400, detail=error_response(90001, "驳回时必须填写审核意见"))

    cr.status = CorrectionStatus.APPROVED if req.action == "approved" else CorrectionStatus.REJECTED
    cr.reviewed_by = current_user.user_id
    cr.review_comment = req.comment
    cr.reviewed_at = datetime.now(timezone.utc)
    await db.flush()

    # 审核后通知提交者（预留通知钩子，后续对接站内信/邮件服务）
    # await NotificationService.notify_correction_result(
    #     user_id=cr.submitted_by,
    #     request_id=cr.request_id,
    #     status=cr.status.value,
    #     comment=cr.review_comment,
    # )

    return success_response(data={
        "request_id": cr.request_id,
        "status": cr.status.value,
        "review_comment": cr.review_comment,
        "reviewed_by": cr.reviewed_by,
        "reviewed_at": str(cr.reviewed_at),
    }, message="审核完成")


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

    # 公告发布后为所有活跃用户创建阅读记录（异步优化可后续改为后台任务）
    from app.models.user import User as UserModel
    user_result = await db.execute(
        select(UserModel.user_id).where(UserModel.status == UserStatus.ACTIVE)
    )
    active_user_ids = [row[0] for row in user_result.all()]
    for uid in active_user_ids:
        db.add(AnnouncementRead(
            read_id=uuid4_str(),
            announcement_id=ann.announcement_id,
            user_id=uid,
            is_read=False,
        ))
    # 将公告和阅读记录在同一事务中提交
    await db.flush()

    return success_response(data={"announcement_id": ann.announcement_id, "title": ann.title}, message="公告发布成功")


@router.get("/announcements")
async def list_announcements(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    priority: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """公告列表（支持按优先级筛选）"""
    conditions = []
    if priority and priority in [p.value for p in Priority]:
        conditions.append(Announcement.priority == Priority(priority))

    query = select(Announcement)
    count_query = select(func.count(Announcement.announcement_id))
    for c in conditions:
        query = query.where(c)
        count_query = count_query.where(c)

    query = query.order_by(desc(Announcement.published_at))

    result = await db.execute(count_query)
    total = result.scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    anns = result.scalars().all()

    # 批量查询当前用户的阅读状态
    ann_ids = [a.announcement_id for a in anns]
    read_status_map = {}
    if ann_ids:
        read_result = await db.execute(
            select(AnnouncementRead).where(
                AnnouncementRead.announcement_id.in_(ann_ids),
                AnnouncementRead.user_id == current_user.user_id,
            )
        )
        for r in read_result.scalars().all():
            read_status_map[r.announcement_id] = r.is_read

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
            "is_read": read_status_map.get(a.announcement_id, False),
        }
        for a in anns
    ]
    return list_response(items=items, page=page, page_size=page_size, total=total)


@router.get("/announcements/unread")
async def get_unread_announcements(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的未读公告列表"""
    result = await db.execute(
        select(Announcement)
        .join(AnnouncementRead, AnnouncementRead.announcement_id == Announcement.announcement_id)
        .where(
            AnnouncementRead.user_id == current_user.user_id,
            AnnouncementRead.is_read == False,
        )
        .order_by(desc(Announcement.published_at))
    )
    anns = result.scalars().all()
    items = [
        {
            "announcement_id": a.announcement_id,
            "title": a.title,
            "content": a.content,
            "priority": a.priority.value,
            "target_type": a.target_type.value,
            "published_at": str(a.published_at) if a.published_at else None,
            "attachment": a.attachment,
        }
        for a in anns
    ]
    return success_response(data={"items": items, "unread_count": len(items)})


@router.post("/announcements/mark-read")
async def mark_announcement_read(
    req: AnnouncementMarkReadRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """标记公告为已读"""
    from datetime import datetime, timezone

    # 查找现有阅读记录
    result = await db.execute(
        select(AnnouncementRead).where(
            AnnouncementRead.announcement_id == req.announcement_id,
            AnnouncementRead.user_id == current_user.user_id,
        )
    )
    read_record = result.scalar_one_or_none()

    if read_record:
        if not read_record.is_read:
            read_record.is_read = True
            read_record.read_at = datetime.now(timezone.utc)
    else:
        # 如果公告存在但用户没有阅读记录，创建一条
        ann = await db.get(Announcement, req.announcement_id)
        if not ann:
            raise HTTPException(status_code=404, detail=error_response(50002, "公告不存在"))
        read_record = AnnouncementRead(
            read_id=uuid4_str(),
            announcement_id=req.announcement_id,
            user_id=current_user.user_id,
            is_read=True,
            read_at=datetime.now(timezone.utc),
        )
        db.add(read_record)

    await db.flush()
    return success_response(data={
        "announcement_id": req.announcement_id,
        "is_read": True,
        "read_at": str(read_record.read_at),
    }, message="已标记为已读")


@router.get("/announcements/{announcement_id}/reads")
async def get_announcement_reads(
    announcement_id: str,
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """公告阅读状态与统计"""
    ann = await db.get(Announcement, announcement_id)
    if not ann:
        raise HTTPException(status_code=404, detail=error_response(50002, "公告不存在"))

    # 阅读统计
    total_result = await db.execute(
        select(func.count(AnnouncementRead.read_id))
        .where(AnnouncementRead.announcement_id == announcement_id)
    )
    total_reads = total_result.scalar() or 0

    read_result = await db.execute(
        select(func.count(AnnouncementRead.read_id))
        .where(
            AnnouncementRead.announcement_id == announcement_id,
            AnnouncementRead.is_read == True,
        )
    )
    read_count = read_result.scalar() or 0
    unread_count = total_reads - read_count

    # 详细阅读记录
    detail_result = await db.execute(
        select(AnnouncementRead).where(AnnouncementRead.announcement_id == announcement_id)
    )
    reads = detail_result.scalars().all()
    items = [
        {
            "read_id": r.read_id,
            "user_id": r.user_id,
            "user_name": r.user.name if r.user else None,
            "is_read": r.is_read,
            "read_at": str(r.read_at) if r.read_at else None,
            "remind_count": r.remind_count,
        }
        for r in reads
    ]

    return success_response(data={
        "announcement_id": announcement_id,
        "title": ann.title,
        "stats": {
            "total": total_reads,
            "read": read_count,
            "unread": unread_count,
            "read_rate": round(read_count / total_reads * 100, 1) if total_reads > 0 else 0.0,
        },
        "items": items,
    })


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
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """查询审计日志（仅管理员）"""
    logs, total = await AuditService.get_logs(
        db_session=db, page=page, page_size=page_size,
        user_id=user_id, action=action,
        resource_type=resource_type, resource_id=resource_id,
        start_date=start_date, end_date=end_date,
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


# ── 员工Excel批量导入 (S1.6) ──

@router.post("/import/employees")
async def import_employees(
    file: UploadFile = File(...),
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Excel批量导入员工账号

    预期Excel格式（第一行为表头）:
    工号 | 姓名 | 部门 | 邮箱 | 手机号 | 入职日期 | 职级
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail=error_response(90001, "仅支持.xlsx/.xls格式"))

    try:
        import io
        import pandas as pd
    except ImportError:
        raise HTTPException(status_code=500, detail=error_response(90004, "服务器缺少openpyxl/pandas依赖"))

    from app.models.user import User
    from app.models.department import Department
    from app.models.audit_log import AuditLog
    from datetime import date

    contents = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(contents), dtype=str)
    except Exception:
        raise HTTPException(status_code=400, detail=error_response(90001, "无法解析Excel文件"))

    col_aliases = {
        '工号': 'employee_id', 'employee_id': 'employee_id', '员工编号': 'employee_id',
        '姓名': 'name', 'name': 'name', '员工姓名': 'name',
        '部门': 'department', 'department': 'department', '部门名称': 'department',
        '邮箱': 'email', 'email': 'email', '电子邮箱': 'email',
        '手机号': 'phone', 'phone': 'phone', '电话': 'phone',
        '入职日期': 'hire_date', 'hire_date': 'hire_date',
        '职级': 'job_level', 'job_level': 'job_level',
    }
    col_map = {}
    for col in df.columns:
        mapped = col_aliases.get(col.strip(), col.strip().lower())
        if mapped in ('employee_id', 'name', 'department', 'email', 'phone', 'hire_date', 'job_level'):
            col_map[mapped] = col

    if 'employee_id' not in col_map or 'name' not in col_map:
        raise HTTPException(status_code=400, detail=error_response(90001, "Excel必须包含工号和姓名列"))

    result = await db.execute(select(Department))
    dept_map = {d.name: d.department_id for d in result.scalars().all()}

    result = await db.execute(select(User.employee_id))
    existing_ids = {r[0] for r in result.all()}

    success_count, fail_count = 0, 0
    failures = []
    default_password = "Hr@123456"

    for idx, (_, row) in enumerate(df.iterrows()):
        eid = str(row.get(col_map['employee_id'], '')).strip()
        name = str(row.get(col_map['name'], '')).strip()

        if not eid or not name:
            fail_count += 1
            failures.append({'row': idx + 2, 'employee_id': eid or '', 'reason': '工号或姓名为空'})
            continue
        if eid in existing_ids:
            fail_count += 1
            failures.append({'row': idx + 2, 'employee_id': eid, 'reason': '工号已存在'})
            continue

        dept_name = str(row.get(col_map.get('department', ''), '')).strip() if 'department' in col_map else ''
        department_id = dept_map.get(dept_name) or next(iter(dept_map.values()), 'dept-001') if dept_map else 'dept-001'

        hire_date_str = str(row.get(col_map.get('hire_date', ''), '')).strip() if 'hire_date' in col_map else ''
        hire_date_val = date.today()
        if hire_date_str:
            try:
                hire_date_val = pd.to_datetime(hire_date_str).date()
            except Exception:
                pass

        try:
            user = User(
                user_id=uuid4_str(), employee_id=eid, name=name,
                email=str(row.get(col_map.get('email', ''), '')).strip() or None if 'email' in col_map else None,
                phone=str(row.get(col_map.get('phone', ''), '')).strip() or None if 'phone' in col_map else None,
                department_id=department_id,
                job_level=str(row.get(col_map.get('job_level', ''), '')).strip() or None if 'job_level' in col_map else None,
                hire_date=hire_date_val,
            )
            user.set_password(default_password)
            db.add(user)
            existing_ids.add(eid)

            audit = AuditLog(
                log_id=uuid4_str(), user_id=user.user_id,
                action="user_import", resource_type="user", resource_id=user.user_id,
                detail={"employee_id": eid, "name": name, "imported_by": current_user.user_id},
            )
            db.add(audit)
            success_count += 1
        except Exception as e:
            fail_count += 1
            failures.append({'row': idx + 2, 'employee_id': eid, 'reason': str(e)[:100]})

    await db.flush()
    return success_response(data={
        "total": len(df),
        "success": success_count,
        "fail": fail_count,
        "failures": failures[:20],
    }, message=f"导入完成: 成功{success_count}人, 失败{fail_count}人")
