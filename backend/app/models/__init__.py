"""所有模型统一导入"""
from app.models.department import Department
from app.models.user import User
from app.models.category import Category
from app.models.document import Document
from app.models.document_sub import DocumentVersion, DocumentChunk
from app.models.faq import FAQ
from app.models.qa_record import QARecord
from app.models.correction import CorrectionRequest
from app.models.announcement import Announcement, AnnouncementRead
from app.models.audit_log import AuditLog
from app.models.employee_data_sensitivity import EmployeeDataSensitivity

__all__ = [
    "Department",
    "User",
    "Category",
    "Document",
    "DocumentVersion",
    "DocumentChunk",
    "FAQ",
    "QARecord",
    "CorrectionRequest",
    "Announcement",
    "AnnouncementRead",
    "AuditLog",
    "EmployeeDataSensitivity",
]
