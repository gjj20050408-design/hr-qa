"""认证接口路由 — /api/v1/auth/* 和 /api/v1/users/me/*"""
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import rate_limit_check
from app.core.security import get_current_user, require_hr_plus
from app.schemas.auth import (
    RegisterRequest, LoginRequest, RefreshTokenRequest, ChangePasswordRequest,
)
from app.schemas.response import success_response, error_response
from app.services.auth_service import AuthService

router = APIRouter(tags=["认证与用户"])

AUTH_PREFIX = "/auth"
USER_PREFIX = "/users"

# 头像上传配置
AVATAR_UPLOAD_DIR = Path(__file__).resolve().parents[3] / "uploads" / "avatars"
AVATAR_URL_PREFIX = "/api/v1/uploads/avatars"  # 与 main.py 中静态挂载路径保持一致
AVATAR_MAX_BYTES = 2 * 1024 * 1024  # 2MB
AVATAR_ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


@router.post(f"{AUTH_PREFIX}/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """员工注册"""
    try:
        user = await AuthService.register(
            employee_id=req.employee_id,
            name=req.name,
            password=req.password,
            department_id=req.department_id,
            email=req.email,
            phone=req.phone,
            db_session=db,
        )
        return success_response(data=user.mask_sensitive(), message="注册成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=error_response(20001, str(e)))


@router.post(f"{AUTH_PREFIX}/login")
async def login(req: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    try:
        # 登录限流：同一账号每60秒最多5次
        if not await rate_limit_check(f"rate:login:{req.account}", 5):
            raise HTTPException(status_code=429, detail=error_response(10006, "请求过于频繁，请稍后再试"))

        result = await AuthService.login(
            account=req.account,
            password=req.password,
            db_session=db,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
        )
        return success_response(data=result, message="登录成功")
    except ValueError as e:
        msg = str(e)
        if "锁定" in msg:
            raise HTTPException(status_code=423, detail=error_response(10004, msg))
        raise HTTPException(status_code=401, detail=error_response(10005, msg))


@router.post(f"{AUTH_PREFIX}/refresh")
async def refresh_token(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """刷新令牌"""
    try:
        result = await AuthService.refresh_token(req.refresh_token, db)
        return success_response(data=result, message="令牌刷新成功")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=error_response(10002, str(e)))


@router.post(f"{AUTH_PREFIX}/logout")
async def logout(current_user=Depends(get_current_user)):
    """退出登录"""
    await AuthService.logout(current_user.user_id)
    return success_response(message="已退出登录")


@router.get(f"{USER_PREFIX}/me")
async def get_me(current_user=Depends(get_current_user)):
    """获取当前用户信息"""
    return success_response(data=current_user.mask_sensitive())


@router.put(f"{USER_PREFIX}/me/password")
async def change_password(
    req: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """修改密码"""
    try:
        await AuthService.change_password(
            user=current_user,
            old_password=req.old_password,
            new_password=req.new_password,
            db_session=db,
        )
        return success_response(message="密码修改成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=error_response(90001, str(e)))


@router.post(f"{USER_PREFIX}/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传当前用户头像

    - 允许格式：jpg / jpeg / png / webp / gif
    - 大小上限：2MB
    - 保存路径：backend/uploads/avatars/<user_id>_<uuid><ext>
    - 返回可访问 URL（通过静态挂载 /api/v1/uploads/avatars 提供）
    """
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in AVATAR_ALLOWED_EXT:
        raise HTTPException(
            status_code=400,
            detail=error_response(90002, f"仅支持 {', '.join(sorted(AVATAR_ALLOWED_EXT))} 格式"),
        )

    # 读取时限制大小，避免超大文件占用内存
    content = await file.read(AVATAR_MAX_BYTES + 1)
    if len(content) > AVATAR_MAX_BYTES:
        raise HTTPException(status_code=400, detail=error_response(90003, "文件大小不能超过 2MB"))

    AVATAR_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # 尝试删除该用户的旧头像文件，避免磁盘堆积（失败忽略即可）
    old_url = current_user.avatar_url or ""
    if old_url.startswith(AVATAR_URL_PREFIX):
        old_path = AVATAR_UPLOAD_DIR / os.path.basename(old_url)
        try:
            if old_path.is_file():
                old_path.unlink()
        except OSError:
            pass

    new_name = f"{current_user.user_id}_{uuid.uuid4().hex}{ext}"
    dest = AVATAR_UPLOAD_DIR / new_name
    try:
        with open(dest, "wb") as f:
            f.write(content)
    except OSError as e:
        raise HTTPException(status_code=500, detail=error_response(90004, f"保存文件失败: {e}"))

    avatar_url = f"{AVATAR_URL_PREFIX}/{new_name}"
    current_user.avatar_url = avatar_url
    await db.commit()

    return success_response(data={"avatar_url": avatar_url}, message="头像更新成功")


@router.delete(f"{USER_PREFIX}/me/avatar")
async def delete_avatar(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除当前用户头像，恢复为默认字母头像"""
    old_url = current_user.avatar_url or ""
    if old_url.startswith(AVATAR_URL_PREFIX):
        old_path = AVATAR_UPLOAD_DIR / os.path.basename(old_url)
        try:
            if old_path.is_file():
                old_path.unlink()
        except OSError:
            pass
    current_user.avatar_url = None
    await db.commit()
    return success_response(message="已恢复默认头像")


@router.get(f"{USER_PREFIX}")
async def list_users(
    page: int = 1, page_size: int = 20,
    keyword: Optional[str] = None,
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """管理员查看用户列表（支持按工号/姓名搜索）"""
    from app.models.user import User
    from sqlalchemy import select, func, or_
    from sqlalchemy.orm import selectinload

    conditions = []
    if keyword and keyword.strip():
        kw = f"%{keyword.strip()}%"
        conditions.append(or_(User.employee_id.ilike(kw), User.name.ilike(kw)))

    count_query = select(func.count(User.user_id))
    for c in conditions:
        count_query = count_query.where(c)
    result = await db.execute(count_query)
    total = result.scalar() or 0

    # 预加载 department 关系，避免 mask_sensitive 触发异步懒加载报错
    query = select(User).options(selectinload(User.department))
    for c in conditions:
        query = query.where(c)
    query = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()

    return success_response(data={
        "items": [u.mask_sensitive() for u in users],
        "pagination": {"page": page, "page_size": page_size, "total": total},
    })
