"""枚举常量定义 — 映射架构设计 L1 §1"""
from enum import Enum


class Role(str, Enum):
    EMPLOYEE = "employee"
    HR_SPECIALIST = "hr_specialist"
    ADMIN = "admin"


class UserStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"


class MaritalStatus(str, Enum):
    SINGLE = "single"
    MARRIED = "married"


class DocFormat(str, Enum):
    PDF = "pdf"
    WORD = "word"
    MARKDOWN = "markdown"
    HTML = "html"


class DocStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class AccessLevel(str, Enum):
    ALL_ROLES = "all_roles"
    HR_ADMIN_ONLY = "hr_admin_only"
    ADMIN_ONLY = "admin_only"


class DocAccessLevel(str, Enum):
    INHERIT = "inherit"
    ALL_ROLES = "all_roles"
    HR_ADMIN_ONLY = "hr_admin_only"
    ADMIN_ONLY = "admin_only"


class CategoryType(str, Enum):
    DOCUMENT = "document"
    FAQ = "faq"


class AnswerType(str, Enum):
    FAQ = "faq"
    RULE = "rule"
    SEARCH = "search"
    RAG = "rag"
    NO_RESULT = "no_result"


class FeedbackType(str, Enum):
    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"


class FAQStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class Priority(str, Enum):
    NORMAL = "normal"
    IMPORTANT = "important"
    URGENT = "urgent"


class TargetType(str, Enum):
    ALL = "all"
    DEPARTMENT = "department"
    ROLE = "role"


class CorrectionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class EmbeddingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SensitivityLevel(str, Enum):
    PUBLIC = "public"
    DEPARTMENT = "department"
    PRIVATE = "private"


class QueryType(str, Enum):
    POLICY_ONLY = "policy_only"
    PERSONAL_DATA = "personal_data"
    MIXED = "mixed"
    AGGREGATION = "aggregation"
    CHITCHAT = "chitchat"
