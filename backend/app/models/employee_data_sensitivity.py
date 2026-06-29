"""员工数据敏感度配置表 EmployeeDataSensitivity（二期预留）"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime
from app.core.database import Base
from app.enums.enums import SensitivityLevel


class EmployeeDataSensitivity(Base):
    __tablename__ = "employee_data_sensitivity"

    field_id = Column(Integer, primary_key=True, autoincrement=True)
    field_name = Column(String(100), nullable=False)
    field_label = Column(String(100), nullable=False)
    sensitivity_level = Column(Enum(SensitivityLevel, values_callable=lambda obj: [e.value for e in obj]), nullable=False, default=SensitivityLevel.PUBLIC)
    source_table = Column(String(100), nullable=False)
    source_column = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<EmployeeDataSensitivity {self.field_label} [{self.sensitivity_level.value}]>"
