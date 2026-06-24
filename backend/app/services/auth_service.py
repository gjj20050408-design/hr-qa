"""认证服务 — 注册、登录、Token 管理"""
import re
import json
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token, create_refresh_token, decode_token,
)
from app.core.config import settings
from app.core.redis import get_redis, rate_limit_check
from app.enums.constants import PASSWORD_POLICY, SECURITY_CONFIG
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.base import uuid4_str


class AuthService:

    @staticmethod
    async def register(
        employee_id: str, name: str, password: str,
        department_id: str, email: Optional[str],
        phone: Optional[str], db_session: AsyncSession,
    ) -> User:
        # 1. 校验格式
        if not re.match(PASSWORD_POLICY["employee_id_pattern"], employee_id):
            raise ValueError("工号格式不正确：4-20位字母数字组合")

        if len(password) < PASSWORD_POLICY["min_length"]:
            raise ValueError(f"密码长度不少于{PASSWORD_POLICY['min_length']}位")

        checks = [
            any(c.isupper() for c in password),
            any(c.islower() for c in password),
            any(c.isdigit() for c in password),
        ]
        if not all(checks):
            raise ValueError("密码需包含大写字母、小写字母和数字")

        if email and not re.match(PASSWORD_POLICY["email_pattern"], email):
            raise ValueError("邮箱格式不正确")

        if phone and not re.match(PASSWORD_POLICY["phone_pattern"], phone):
            raise ValueError("手机号格式不正确")

        # 2. 检查唯一性
        result = await db_session.execute(
            select(User).where(User.employee_id == employee_id)
        )
        if result.scalar_one_or_none():
            raise ValueError("工号已存在")

        # 3. 创建用户
        user = User(
            user_id=uuid4_str(),
            employee_id=employee_id,
            name=name,
            email=email,
            phone=phone,
            department_id=department_id,
        )
        user.set_password(password)
        db_session.add(user)

        # 4. 审计日志
        audit = AuditLog(
            log_id=uuid4_str(),
            user_id=user.user_id,
            action="user_register",
            resource_type="user",
            resource_id=user.user_id,
            detail={"employee_id": employee_id, "name": name},
        )
        db_session.add(audit)
        await db_session.flush()
        return user

    @staticmethod
    async def login(
        account: str, password: str, db_session: AsyncSession,
        ip_address: str = None, user_agent: str = None,
    ) -> dict:
        # 1. 查找用户
        result = await db_session.execute(
            select(User).where(
                (User.employee_id == account) | (User.email == account)
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("账号或密码错误")

        if user.status.value != "active":
            raise ValueError("账号已禁用")

        # 2. 检查锁定
        if user.is_locked():
            remaining = int((user.locked_until - datetime.utcnow()).total_seconds() / 60)
            raise ValueError(f"账号已锁定，请{remaining}分钟后重试")

        # 3. 验证密码
        if not user.verify_password(password):
            user.record_failed_attempt()
            audit = AuditLog(
                log_id=uuid4_str(), user_id=user.user_id,
                action="login_failed", resource_type="user", resource_id=user.user_id,
                detail={"attempt": user.login_attempts},
                ip_address=ip_address, user_agent=user_agent,
            )
            db_session.add(audit)
            await db_session.flush()
            remaining = SECURITY_CONFIG["max_login_attempts"] - user.login_attempts
            raise ValueError(f"密码错误，剩余尝试次数: {max(0, remaining)}")

        # 4. 生成 Token
        user.reset_login_attempts()
        access_token = create_access_token(user.user_id, user.role.value)
        refresh_token = create_refresh_token(user.user_id)

        # 5. 缓存到 Redis
        try:
            r = await get_redis()
            await r.setex(
                f"session:{user.user_id}",
                SECURITY_CONFIG["access_token_expire_minutes"] * 60,
                json.dumps({"user_id": user.user_id, "role": user.role.value}),
            )
            # 存储 refresh token
            await r.setex(
                f"refresh:{user.user_id}",
                SECURITY_CONFIG["refresh_token_expire_days"] * 86400,
                refresh_token,
            )
        except Exception:
            pass

        # 6. 审计日志
        audit = AuditLog(
            log_id=uuid4_str(), user_id=user.user_id,
            action="login_success", resource_type="user", resource_id=user.user_id,
            ip_address=ip_address, user_agent=user_agent,
        )
        db_session.add(audit)
        await db_session.flush()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user.mask_sensitive(),
        }

    @staticmethod
    async def refresh_token(refresh_token: str, db_session: AsyncSession) -> dict:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("无效的 Refresh Token")

        user_id = payload.get("sub")
        user = await db_session.get(User, user_id)
        if not user or user.status.value != "active":
            raise ValueError("用户不存在或已禁用")

        # 验证 refresh token 与 Redis 中一致
        try:
            r = await get_redis()
            stored = await r.get(f"refresh:{user_id}")
            if stored != refresh_token:
                raise ValueError("Refresh Token 已被使用或失效")
        except Exception:
            pass

        # 生成新的 token pair
        new_access = create_access_token(user.user_id, user.role.value)
        new_refresh = create_refresh_token(user.user_id)

        try:
            r = await get_redis()
            await r.setex(f"refresh:{user_id}", SECURITY_CONFIG["refresh_token_expire_days"] * 86400, new_refresh)
            await r.setex(f"session:{user_id}", SECURITY_CONFIG["access_token_expire_minutes"] * 60,
                          json.dumps({"user_id": user.user_id, "role": user.role.value}))
        except Exception:
            pass

        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "token_type": "bearer",
        }

    @staticmethod
    async def logout(user_id: str) -> None:
        try:
            r = await get_redis()
            await r.delete(f"session:{user_id}")
            await r.delete(f"refresh:{user_id}")
        except Exception:
            pass

    @staticmethod
    async def change_password(
        user: User, old_password: str, new_password: str, db_session: AsyncSession,
    ) -> None:
        if not user.verify_password(old_password):
            raise ValueError("旧密码错误")
        if len(new_password) < PASSWORD_POLICY["min_length"]:
            raise ValueError(f"密码长度不少于{PASSWORD_POLICY['min_length']}位")
        checks = [
            any(c.isupper() for c in new_password),
            any(c.islower() for c in new_password),
            any(c.isdigit() for c in new_password),
        ]
        if not all(checks):
            raise ValueError("密码需包含大写字母、小写字母和数字")

        user.set_password(new_password)
        audit = AuditLog(
            log_id=uuid4_str(), user_id=user.user_id,
            action="change_password", resource_type="user", resource_id=user.user_id,
        )
        db_session.add(audit)
        await db_session.flush()
