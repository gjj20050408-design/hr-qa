"""认证相关 Schema"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.enums.constants import PASSWORD_POLICY


class RegisterRequest(BaseModel):
    """注册请求"""
    employee_id: str = Field(..., min_length=4, max_length=20, description="工号")
    name: str = Field(..., min_length=2, max_length=50, description="姓名")
    password: str = Field(..., min_length=8, description="密码")
    department_id: str = Field(..., description="部门ID")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")

    @field_validator("employee_id")
    @classmethod
    def validate_employee_id(cls, v: str) -> str:
        import re
        if not re.match(PASSWORD_POLICY["employee_id_pattern"], v):
            raise ValueError("工号格式不正确：4-20位字母数字组合")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < PASSWORD_POLICY["min_length"]:
            raise ValueError(f"密码长度不少于{PASSWORD_POLICY['min_length']}位")
        checks = [
            any(c.isupper() for c in v),
            any(c.islower() for c in v),
            any(c.isdigit() for c in v),
        ]
        if not all(checks):
            raise ValueError("密码需包含大写字母、小写字母和数字")
        return v


class LoginRequest(BaseModel):
    """登录请求"""
    account: str = Field(..., description="工号或邮箱")
    password: str = Field(..., description="密码")


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str = Field(..., description="Refresh Token")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=8, description="新密码")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < PASSWORD_POLICY["min_length"]:
            raise ValueError(f"密码长度不少于{PASSWORD_POLICY['min_length']}位")
        checks = [
            any(c.isupper() for c in v),
            any(c.islower() for c in v),
            any(c.isdigit() for c in v),
        ]
        if not all(checks):
            raise ValueError("密码需包含大写字母、小写字母和数字")
        return v


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
