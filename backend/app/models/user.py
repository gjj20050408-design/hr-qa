"""用户表 User — 完整 ORM 模型"""
from datetime import datetime, timedelta, date, timezone
from sqlalchemy import Column, String, Integer, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.security import hash_password, verify_password as vp
from app.models.base import uuid4_str
from app.enums.enums import Role, UserStatus, MaritalStatus
from app.enums.constants import SECURITY_CONFIG


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(64), primary_key=True, default=uuid4_str)
    employee_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=True, index=True)
    phone = Column(String(15), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(Role), nullable=False, default=Role.EMPLOYEE)
    department_id = Column(String(64), ForeignKey("departments.department_id"), nullable=False)
    job_level = Column(String(20), nullable=True)
    hire_date = Column(Date, nullable=False)
    work_location = Column(String(50), nullable=True)
    marital_status = Column(Enum(MaritalStatus), nullable=True)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    department = relationship("Department", back_populates="users")

    def set_password(self, plain: str) -> None:
        self.password_hash = hash_password(plain)

    def verify_password(self, plain: str) -> bool:
        return vp(plain, self.password_hash)

    def is_locked(self) -> bool:
        if self.locked_until and datetime.now(timezone.utc) < self.locked_until:
            return True
        if self.locked_until and datetime.now(timezone.utc) >= self.locked_until:
            self.locked_until = None
            self.login_attempts = 0
        return False

    def record_failed_attempt(self) -> None:
        self.login_attempts += 1
        max_attempts = SECURITY_CONFIG.get("max_login_attempts", 5)
        if self.login_attempts >= max_attempts:
            self.locked_until = datetime.now(timezone.utc) + timedelta(
                minutes=SECURITY_CONFIG.get("lockout_duration_minutes", 30)
            )

    def reset_login_attempts(self) -> None:
        self.login_attempts = 0
        self.locked_until = None

    def mask_sensitive(self) -> dict:
        data = {
            "user_id": self.user_id,
            "employee_id": self.employee_id,
            "name": self.name,
            "role": self.role.value if self.role else None,
            "department_name": self.department.name if self.department else None,
            "department_id": self.department_id,
            "job_level": self.job_level,
            "hire_date": str(self.hire_date) if self.hire_date else None,
            "work_location": self.work_location,
            "marital_status": self.marital_status.value if self.marital_status else None,
            "status": self.status.value if self.status else None,
        }
        if self.phone:
            data["phone"] = self.phone[:3] + "****" + self.phone[-4:]
        if self.email:
            parts = self.email.split("@")
            data["email"] = parts[0][0] + "***@" + parts[1] if len(parts) == 2 else self.email
        return data

    def compute_tenure_years(self) -> int:
        today = datetime.now(timezone.utc).date()
        years = today.year - self.hire_date.year
        if today.month < self.hire_date.month or (
            today.month == self.hire_date.month and today.day < self.hire_date.day
        ):
            years -= 1
        return max(0, years)

    def __repr__(self):
        return f"<User {self.name} ({self.employee_id})>"
