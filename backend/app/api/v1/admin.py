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
from app.models.audit_log import AuditLog
from app.models.base import uuid4_str
from app.schemas.auth import UserUpdateRequest
from app.enums.enums import CorrectionStatus, Priority, TargetType, UserStatus, Role
from sqlalchemy import select, func, desc, or_
from sqlalchemy.orm import selectinload

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

    # 审核完成后，通过站内通知告知提交者审核结果（批准/驳回均通知）
    from app.models.document import Document
    doc = await db.get(Document, cr.document_id)
    doc_title = doc.title if doc else cr.document_id
    if cr.status == CorrectionStatus.APPROVED:
        notify_title = "您的纠错反馈已被批准"
        notify_content = f"您针对制度文档《{doc_title}》「{cr.section}」提交的纠错反馈已被批准。"
    else:
        notify_title = "您的纠错反馈已被驳回"
        notify_content = f"您针对制度文档《{doc_title}》「{cr.section}」提交的纠错反馈未被采纳。"
    if cr.review_comment:
        notify_content += f"\n审核意见：{cr.review_comment}"

    notify = Announcement(
        announcement_id=uuid4_str(),
        title=notify_title,
        content=notify_content,
        priority=Priority.IMPORTANT,
        target_type=TargetType.ROLE,
        target_ids=[cr.submitted_by],
        published_by=current_user.user_id,
    )
    db.add(notify)
    db.add(AnnouncementRead(
        read_id=uuid4_str(),
        announcement_id=notify.announcement_id,
        user_id=cr.submitted_by,
        is_read=False,
    ))
    await db.flush()

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
    """公告列表（支持按优先级筛选）

    可见性：仅返回当前用户拥有阅读记录（AnnouncementRead）的公告。
    全员公告在发布时已为每个活跃用户建立阅读记录，定向通知（如纠错审核结果）
    仅为目标用户建立记录，因此本接口天然只向对应用户展示其应见的公告。
    """
    conditions = [AnnouncementRead.user_id == current_user.user_id]
    if priority and priority in [p.value for p in Priority]:
        conditions.append(Announcement.priority == Priority(priority))

    query = (
        select(Announcement, AnnouncementRead.is_read)
        .join(AnnouncementRead, AnnouncementRead.announcement_id == Announcement.announcement_id)
        .options(selectinload(Announcement.publisher))
    )
    count_query = (
        select(func.count(Announcement.announcement_id))
        .join(AnnouncementRead, AnnouncementRead.announcement_id == Announcement.announcement_id)
    )
    for c in conditions:
        query = query.where(c)
        count_query = count_query.where(c)

    query = query.order_by(desc(Announcement.published_at))

    result = await db.execute(count_query)
    total = result.scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    rows = result.all()

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
            "is_read": bool(is_read),
        }
        for a, is_read in rows
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
        # 没有阅读记录即表示该公告对当前用户不可见（如面向他人的定向通知），
        # 不再补建记录，避免越权标记/暴露本不应可见的公告。
        raise HTTPException(status_code=404, detail=error_response(50002, "公告不存在"))

    await db.flush()
    return success_response(data={
        "announcement_id": req.announcement_id,
        "is_read": True,
        "read_at": str(read_record.read_at),
    }, message="已标记为已读")


@router.post("/announcements/mark-all-read")
async def mark_all_announcements_read(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """将当前用户的全部公告标记为已读"""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)

    # 仅标记当前用户已拥有阅读记录的公告。用户可见的公告（全员公告发布时、
    # 定向通知创建时）均已建立阅读记录，因此无需为其补建记录——否则会把
    # 面向他人的定向通知（如纠错审核结果）错误地暴露给当前用户。
    result = await db.execute(
        select(AnnouncementRead).where(
            AnnouncementRead.user_id == current_user.user_id,
            AnnouncementRead.is_read == False,
        )
    )
    updated = 0
    for r in result.scalars().all():
        r.is_read = True
        r.read_at = now
        updated += 1

    await db.flush()
    return success_response(data={"updated": updated}, message="已全部标记为已读")


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
        select(AnnouncementRead)
        .options(selectinload(AnnouncementRead.user).selectinload(User.department))
        .where(AnnouncementRead.announcement_id == announcement_id)
    )
    reads = detail_result.scalars().all()
    items = [
        {
            "read_id": r.read_id,
            "user_id": r.user_id,
            "employee_id": r.user.employee_id if r.user else None,
            "name": r.user.name if r.user else None,
            "user_name": r.user.name if r.user else None,
            "department_name": (r.user.department.name if r.user and r.user.department else None),
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
            "user_name": l.user.name if l.user else None,
            "employee_id": l.user.employee_id if l.user else None,
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
    default_password = DEFAULT_PASSWORD

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


# ── 用户管理（编辑 / 禁用） ──

@router.get("/departments")
async def list_departments(
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """部门列表（用于用户编辑时选择部门）"""
    from app.models.department import Department
    result = await db.execute(
        select(Department).order_by(Department.sort_order, Department.name)
    )
    departments = result.scalars().all()
    return success_response(data={
        "items": [
            {"department_id": d.department_id, "name": d.name, "parent_id": d.parent_id}
            for d in departments
        ]
    })


@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    req: UserUpdateRequest,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """修改用户信息（仅管理员）"""
    result = await db.execute(
        select(User).options(selectinload(User.department)).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail=error_response(90003, "用户不存在"))

    # 禁止管理员修改自己的角色/状态，避免误操作把自己锁在门外
    if user_id == current_user.user_id and (req.role is not None or req.status is not None):
        raise HTTPException(status_code=400, detail=error_response(90001, "不能修改自己的角色或状态"))

    # 校验部门存在
    if req.department_id is not None:
        from app.models.department import Department
        dept = await db.get(Department, req.department_id)
        if not dept:
            raise HTTPException(status_code=400, detail=error_response(90001, "部门不存在"))
        user.department_id = req.department_id

    changed = {}
    if req.name is not None:
        user.name = req.name
        changed["name"] = req.name
    if req.email is not None:
        user.email = req.email
        changed["email"] = req.email
    if req.phone is not None:
        user.phone = req.phone
        changed["phone"] = req.phone
    if req.job_level is not None:
        user.job_level = req.job_level
        changed["job_level"] = req.job_level
    if req.department_id is not None:
        changed["department_id"] = req.department_id
    if req.role is not None:
        user.role = Role(req.role)
        changed["role"] = req.role
    if req.status is not None:
        user.status = UserStatus(req.status)
        changed["status"] = req.status

    await db.flush()

    db.add(AuditLog(
        log_id=uuid4_str(), user_id=current_user.user_id,
        action="user_update", resource_type="user", resource_id=user_id,
        detail={"changed": changed},
    ))
    await db.flush()

    # 重新加载 department 以正确脱敏返回
    await db.refresh(user, attribute_names=["department"])
    return success_response(data=user.mask_sensitive(), message="用户信息已更新")


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """禁用用户（软删除 —— 置为 disabled，保留历史数据与审计追溯）"""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=error_response(90003, "用户不存在"))
    if user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail=error_response(90001, "不能禁用自己的账号"))
    if user.status == UserStatus.DISABLED:
        raise HTTPException(status_code=409, detail=error_response(90001, "该用户已被禁用"))

    user.status = UserStatus.DISABLED
    await db.flush()

    db.add(AuditLog(
        log_id=uuid4_str(), user_id=current_user.user_id,
        action="user_disable", resource_type="user", resource_id=user_id,
        detail={"employee_id": user.employee_id, "name": user.name},
    ))
    await db.flush()
    return success_response(message="用户已禁用")


# 员工账号导入及后续重置时使用的默认密码（与 import_employees 保持一致）
DEFAULT_PASSWORD = "Hr@123456"


@router.post("/users/{user_id}/unlock")
async def unlock_user(
    user_id: str,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """解锁用户（清除因连续登录失败导致的锁定，仅管理员）"""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=error_response(90003, "用户不存在"))

    user.reset_login_attempts()
    await db.flush()

    db.add(AuditLog(
        log_id=uuid4_str(), user_id=current_user.user_id,
        action="user_unlock", resource_type="user", resource_id=user_id,
        detail={"employee_id": user.employee_id, "name": user.name},
    ))
    await db.flush()
    return success_response(message="用户已解锁")


@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: str,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """重置用户密码为默认密码，并解除锁定（仅管理员）"""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=error_response(90003, "用户不存在"))

    user.set_password(DEFAULT_PASSWORD)
    # 重置密码时一并解除锁定，避免用户拿到新密码仍被锁在门外
    user.reset_login_attempts()
    await db.flush()

    db.add(AuditLog(
        log_id=uuid4_str(), user_id=current_user.user_id,
        action="user_reset_password", resource_type="user", resource_id=user_id,
        detail={"employee_id": user.employee_id, "name": user.name},
    ))
    await db.flush()
    return success_response(
        data={"default_password": DEFAULT_PASSWORD},
        message="密码已重置为默认密码，请提醒用户尽快修改",
    )


# ── 问答质量闭环：待优化问题 → 生成 FAQ 草稿 ──

@router.get("/insights/faq-candidates")
async def get_faq_candidates(
    limit: int = Query(10, ge=1, le=50),
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """待优化问题列表：答不出或被评为无帮助的高频提问（HR/管理员）"""
    from app.services.qa_insight_service import QAInsightService
    candidates = await QAInsightService.get_faq_candidates(db_session=db, limit=limit)
    return success_response(data={"items": candidates})


@router.post("/insights/faq-draft")
async def generate_faq_draft(
    body: dict,
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """根据一条待优化问题，用 LLM 生成 FAQ 草稿（不落库，供 HR 编辑后再发布）"""
    from app.services.qa_insight_service import QAInsightService
    question = (body or {}).get("question", "").strip()
    if not question:
        raise HTTPException(status_code=400, detail=error_response(90001, "问题不能为空"))

    draft = await QAInsightService.generate_faq_draft(question=question, db_session=db)
    if draft is None:
        raise HTTPException(status_code=503, detail=error_response(90004, "LLM 服务暂不可用，无法生成草稿"))
    return success_response(data=draft, message="草稿已生成，请审核后发布")
