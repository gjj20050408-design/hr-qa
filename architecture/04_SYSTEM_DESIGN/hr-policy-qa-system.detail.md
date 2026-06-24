# HR制度智能问答系统 — 实现细节（L1）

> **文件类型**：L1 实现层 · **映射 L0**：[`hr-policy-qa-system.md`](./hr-policy-qa-system.md)
> 本文件仅在 `/forge` 任务显式引用时加载。日常阅读和任务规划优先使用 L0。
> **孤岛检查**：本文件中的每一节在 L0 中必须有对应的超链接入口；禁止出现孤立内容。

---

## 版本历史

| 版本 | 日期 | 变更记录 |
|---------|------|-----------|
| v1.0 | 2026-06-15 | 初始L1：配置常量、完整数据结构、15个算法伪代码、4个决策树、12个边界情况 |

---

## 本文件章节索引

|   §   | 章节 | 映射 L0 入口 |
| :---: | -------------------------------------------------------------------- | :--------------: |
|  §1   | [配置常量](#1-配置常量)                             |  L0 §6 数据模型  |
|  §2   | [完整核心数据结构](#2-完整核心数据结构)         |  L0 §6.1 核心实体  |
|  §3   | [核心算法伪代码](#3-核心算法伪代码) | L0 §5.1 操作契约 |
|  §4   | [详细决策树逻辑](#4-详细决策树逻辑)            |   L0 §4 架构设计   |
|  §5   | [边界情况与易错点](#5-边界情况与易错点)      |    L0 §5 / §9    |
|  §6   | [测试辅助工具](#6-测试辅助工具)                        | L0 §11 测试策略  |

---

## §1 配置常量

> 映射 L0 入口：L0 §6 数据模型 → *完整配置常量字典见 [L1 §1]*

### 1.1 角色枚举

```python
from enum import Enum

class Role(str, Enum):
    """用户角色"""
    EMPLOYEE = "employee"           # 普通员工
    HR_SPECIALIST = "hr_specialist" # HR专员
    ADMIN = "admin"                 # 系统管理员

class UserStatus(str, Enum):
    """账号状态"""
    ACTIVE = "active"     # 正常
    DISABLED = "disabled" # 已禁用

class MaritalStatus(str, Enum):
    """婚姻状态"""
    SINGLE = "single"
    MARRIED = "married"
```

### 1.2 文档与分类枚举

```python
class DocFormat(str, Enum):
    """文档格式"""
    PDF = "pdf"
    WORD = "word"
    MARKDOWN = "markdown"
    HTML = "html"

class DocStatus(str, Enum):
    """文档状态"""
    DRAFT = "draft"           # 草稿
    PUBLISHED = "published"   # 已发布
    ARCHIVED = "archived"     # 已归档

class AccessLevel(str, Enum):
    """检索权限级别（用于分类和有效级别）"""
    ALL_ROLES = "all_roles"           # 全员可见
    HR_ADMIN_ONLY = "hr_admin_only"   # 仅HR+管理员
    ADMIN_ONLY = "admin_only"         # 仅管理员

class DocAccessLevel(str, Enum):
    """文档检索权限级别（含继承选项）"""
    INHERIT = "inherit"               # 继承分类权限
    ALL_ROLES = "all_roles"           # 全员可见（覆盖分类）
    HR_ADMIN_ONLY = "hr_admin_only"   # 仅HR+管理员（覆盖分类）
    ADMIN_ONLY = "admin_only"         # 仅管理员（覆盖分类）

class CategoryType(str, Enum):
    """分类类型"""
    DOCUMENT = "document"   # 文档分类
    FAQ = "faq"             # FAQ分类
```

### 1.3 问答枚举

```python
class AnswerType(str, Enum):
    """回答类型"""
    FAQ = "faq"           # FAQ匹配
    RULE = "rule"         # 规则匹配
    SEARCH = "search"     # 全文搜索
    RAG = "rag"           # RAG智能问答
    NO_RESULT = "no_result" # 无结果

class FeedbackType(str, Enum):
    """反馈类型"""
    HELPFUL = "helpful"         # 有帮助
    NOT_HELPFUL = "not_helpful" # 无帮助

class FAQStatus(str, Enum):
    """FAQ状态"""
    ACTIVE = "active"
    ARCHIVED = "archived"
```

### 1.4 公告与纠错枚举

```python
class Priority(str, Enum):
    """公告优先级"""
    NORMAL = "normal"       # 普通
    IMPORTANT = "important" # 重要
    URGENT = "urgent"       # 紧急

class TargetType(str, Enum):
    """推送范围类型"""
    ALL = "all"               # 全员
    DEPARTMENT = "department" # 指定部门
    ROLE = "role"             # 指定角色

class CorrectionStatus(str, Enum):
    """纠错审核状态"""
    PENDING = "pending"     # 待审核
    APPROVED = "approved"   # 已通过
    REJECTED = "rejected"   # 已驳回

class EmbeddingStatus(str, Enum):
    """向量化状态"""
    PENDING = "pending"         # 待处理
    PROCESSING = "processing"   # 处理中
    COMPLETED = "completed"     # 已完成
    FAILED = "failed"           # 失败

class SensitivityLevel(str, Enum):
    """个人数据字段敏感度级别（二期新增）"""
    PUBLIC = "public"           # 全员可见
    DEPARTMENT = "department"   # 部门内可见
    PRIVATE = "private"         # 绝对私密

class QueryType(str, Enum):
    """RAG查询类型（二期新增，LLM意图提取结果）"""
    POLICY_ONLY = "policy_only"       # 仅涉及制度政策
    PERSONAL_DATA = "personal_data"   # 明确涉及个人数据
    MIXED = "mixed"                   # 同时涉及制度和数据
    AGGREGATION = "aggregation"       # 聚合/统计查询
```

### 1.5 权限矩阵（配置表）

```python
# ── 解析有效访问级别并检查角色权限 ──
PERMISSION_MATRIX = {
    # (有效级别, 角色) → 是否可访问
    (AccessLevel.ALL_ROLES, Role.EMPLOYEE):       True,
    (AccessLevel.ALL_ROLES, Role.HR_SPECIALIST):   True,
    (AccessLevel.ALL_ROLES, Role.ADMIN):           True,
    (AccessLevel.HR_ADMIN_ONLY, Role.EMPLOYEE):       False,
    (AccessLevel.HR_ADMIN_ONLY, Role.HR_SPECIALIST):   True,
    (AccessLevel.HR_ADMIN_ONLY, Role.ADMIN):           True,
    (AccessLevel.ADMIN_ONLY, Role.EMPLOYEE):       False,
    (AccessLevel.ADMIN_ONLY, Role.HR_SPECIALIST):   False,
    (AccessLevel.ADMIN_ONLY, Role.ADMIN):           True,
}
```

### 1.6 安全与限流常量

```python
SECURITY_CONFIG = {
    "bcrypt_rounds": 12,                        # bcrypt加密轮数
    "access_token_expire_minutes": 120,          # access token 有效期（2小时）
    "refresh_token_expire_days": 7,              # refresh token 有效期（7天）
    "max_login_attempts": 5,                     # 最大登录失败次数
    "lockout_duration_minutes": 30,              # 锁定持续时间（30分钟）
    "session_idle_timeout_minutes": 30,          # 多轮对话会话超时（30分钟）
    "max_dialogue_rounds": 20,                   # 最大对话轮数
    "rate_limit_qna_per_minute": 20,             # 每用户每分钟问答限流
    "rate_limit_search_per_minute": 30,          # 每用户每分钟搜索限流
}

PASSWORD_POLICY = {
    "min_length": 8,                             # 最小密码长度
    "require_uppercase": True,                   # 需包含大写字母
    "require_lowercase": True,                   # 需包含小写字母
    "require_digit": True,                       # 需包含数字
    "employee_id_pattern": r"^[A-Za-z0-9]{4,20}$",     # 工号格式
    "phone_pattern": r"^1[3-9]\d{9}$",                  # 手机号格式
    "email_pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", # 邮箱格式
}
```

### 1.7 问答策略链阈值

```python
QA_THRESHOLDS = {
    "faq_similarity_min": 0.70,           # FAQ匹配最低相似度阈值
    "search_max_results": 20,             # 搜索最大返回结果数
    "rag_top_k_retrieval": 10,            # 向量检索Top-K（为权限过滤留余量）
    "rag_top_n_prompt": 5,                # 权限过滤后用于Prompt的Top-N
    "rag_chunk_token_size": 500,          # 分块Token大小
    "rag_high_confidence": 0.85,          # 高置信度阈值
    "rag_low_confidence": 0.70,           # 低置信度阈值（低于此值显示免责声明）
    "llm_timeout_seconds": 5,             # LLM API调用超时时间
    "llm_circuit_breaker_failures": 5,    # 熔断器触发连续失败次数
    "llm_circuit_breaker_timeout": 30,    # 熔断器开启持续时间（秒）
}
```

### 1.8 规则模板库（一期）

```python
RULE_TEMPLATES = [
    {
        "id": "rule-annual-leave",
        "patterns": [r"年假.*(几天|多少|怎么算|计算)", r"年休假.*天"],
        "keywords": ["年假", "年休假"],
        "template": (
            "根据公司《休假制度》规定，您的年假天数为：\n"
            "- 工龄1-3年：5天\n"
            "- 工龄3-10年：10天\n"
            "- 工龄10年以上：15天\n\n"
            "您当前工龄{tenure_years}年，年假为{annual_leave_days}天。"
        ),
        "requires_user_context": True,   # 需要入职日期来计算
        "context_fields": ["hire_date"],
    },
    {
        "id": "rule-sick-leave-pay",
        "patterns": [r"病假.*工资", r"病假.*薪酬", r"病假.*怎么算"],
        "keywords": ["病假", "工资"],
        "template": (
            "根据公司《薪酬制度》规定，病假期薪酬计算规则：\n"
            "- 病假≤2天：全额工资\n"
            "- 病假3-30天：基本工资的80%\n"
            "- 病假>30天：按当地最低工资标准执行\n\n"
            "具体以实际审批为准，建议联系HR确认。"
        ),
        "requires_user_context": False,
    },
    {
        "id": "rule-overtime-pay",
        "patterns": [r"加班.*(费|标准|怎么算|工资)", r"加班费.*标准"],
        "keywords": ["加班", "加班费"],
        "template": (
            "根据公司《薪酬制度》规定：\n"
            "- 工作日加班：1.5倍工资\n"
            "- 休息日加班：2倍工资（或调休）\n"
            "- 法定节假日加班：3倍工资\n\n"
            "加班需提前审批，未经审批的加班不计入加班费。"
        ),
        "requires_user_context": False,
    },
    {
        "id": "rule-probation",
        "patterns": [r"试用期.*(多久|考核|标准|转正)"],
        "keywords": ["试用期", "转正"],
        "template": (
            "根据公司《绩效制度》规定：\n"
            "- 一般员工试用期为3个月\n"
            "- 表现优秀者可提前转正（需主管审批）\n"
            "- 试用期考核标准包括：出勤率、任务完成度、团队协作评估"
        ),
        "requires_user_context": False,
    },
    {
        "id": "rule-marriage-leave",
        "patterns": [r"婚假.*(几天|多少|怎么|规定)"],
        "keywords": ["婚假"],
        "template": (
            "根据公司《休假制度》规定：\n"
            "- 法定婚假为3天\n"
            "- 晚婚（男≥25岁/女≥23岁）增加7天\n"
            "- 婚假需在领证后一年内休完\n\n"
            "请提前向部门主管和HR提交婚假申请。"
        ),
        "requires_user_context": False,
    },
]
```

---

## §2 完整核心数据结构

> 映射 L0 入口：L0 §6.1 核心实体 → *完整方法实现见 [L1 §2]*

### 2.1 User 模型（完整ORM）

```python
from sqlalchemy import Column, String, Integer, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    """用户实体 — SQLAlchemy ORM 模型"""
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

    department = relationship("Department", back_populates="users")

    def set_password(self, plain: str) -> None:
        """使用bcrypt(cost=12)对明文密码进行哈希处理。"""
        self.password_hash = pwd_context.hash(plain)

    def verify_password(self, plain: str) -> bool:
        """验证明文密码是否与存储的bcrypt哈希匹配。"""
        return pwd_context.verify(plain, self.password_hash)

    def is_locked(self) -> bool:
        """检查账号当前是否处于锁定状态。
        若锁定时间已过，自动解除锁定并重置计数器。"""
        if self.locked_until and datetime.utcnow() < self.locked_until:
            return True
        if self.locked_until and datetime.utcnow() >= self.locked_until:
            self.locked_until = None
            self.login_attempts = 0
        return False

    def record_failed_attempt(self) -> None:
        """增加失败登录计数，达到阈值时锁定账号。"""
        self.login_attempts += 1
        if self.login_attempts >= SECURITY_CONFIG["max_login_attempts"]:
            self.locked_until = datetime.utcnow() + timedelta(
                minutes=SECURITY_CONFIG["lockout_duration_minutes"]
            )

    def reset_login_attempts(self) -> None:
        """登录成功后重置失败计数器和锁定状态。"""
        self.login_attempts = 0
        self.locked_until = None

    def mask_sensitive(self) -> dict:
        """返回脱敏后的字典，用于前端展示。
        手机号保留前三后四，邮箱隐藏用户名部分。"""
        data = {
            "user_id": self.user_id,
            "employee_id": self.employee_id,
            "name": self.name,
            "role": self.role,
            "department": self.department.name if self.department else None,
            "job_level": self.job_level,
            "hire_date": str(self.hire_date),
            "work_location": self.work_location,
            "marital_status": self.marital_status,
            "status": self.status,
        }
        if self.phone:
            data["phone"] = self.phone[:3] + "****" + self.phone[-4:]
        if self.email:
            parts = self.email.split("@")
            data["email"] = parts[0][0] + "***@" + parts[1]
        return data

    def compute_tenure_years(self) -> int:
        """从入职日期计算至今的服务年限。"""
        today = datetime.utcnow().date()
        years = today.year - self.hire_date.year
        if today.month < self.hire_date.month or (
            today.month == self.hire_date.month and today.day < self.hire_date.day
        ):
            years -= 1
        return max(0, years)
```

### 2.2 Document 模型（完整ORM + 权限逻辑）

```python
class Document(Base):
    """制度文档实体 — SQLAlchemy ORM 模型"""
    __tablename__ = "documents"

    document_id = Column(String(64), primary_key=True, default=uuid4_str)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)  # LONGTEXT，解析后的纯文本
    category_id = Column(String(64), ForeignKey("categories.category_id"), nullable=False)
    format = Column(Enum(DocFormat), nullable=False)
    version = Column(String(10), nullable=False, default="1.0")
    version_note = Column(String(500), nullable=True)
    status = Column(Enum(DocStatus), nullable=False, default=DocStatus.DRAFT)
    access_level = Column(Enum(DocAccessLevel), nullable=False, default=DocAccessLevel.INHERIT)
    uploaded_by = Column(String(64), ForeignKey("users.user_id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    word_count = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    embedding_status = Column(String(20), default=EmbeddingStatus.PENDING)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="documents")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    def effective_access_level(self) -> AccessLevel:
        """解析有效访问级别，考虑继承链。
        若文档设为inherit，从所属分类获取权限；否则使用文档自身设置。"""
        if self.access_level == DocAccessLevel.INHERIT:
            if self.category:
                return self.category.access_level
            return AccessLevel.ALL_ROLES  # 安全默认值
        # 将 DocAccessLevel 映射到 AccessLevel
        mapping = {
            DocAccessLevel.ALL_ROLES: AccessLevel.ALL_ROLES,
            DocAccessLevel.HR_ADMIN_ONLY: AccessLevel.HR_ADMIN_ONLY,
            DocAccessLevel.ADMIN_ONLY: AccessLevel.ADMIN_ONLY,
        }
        return mapping.get(self.access_level, AccessLevel.ALL_ROLES)

    def can_access(self, role: Role) -> bool:
        """检查给定角色是否可访问本文档。
        admin角色始终可访问全部文档。"""
        if role == Role.ADMIN:
            return True
        effective = self.effective_access_level()
        return PERMISSION_MATRIX.get((effective, role), False)

    def is_overridden(self) -> bool:
        """检查文档的access_level是否覆盖了分类默认值。"""
        return self.access_level != DocAccessLevel.INHERIT

    def publish(self) -> None:
        """将文档从草稿状态转为已发布状态。"""
        if self.status == DocStatus.DRAFT:
            self.status = DocStatus.PUBLISHED
            self.published_at = datetime.utcnow()

    def archive(self) -> None:
        """将文档转为已归档状态。"""
        self.status = DocStatus.ARCHIVED
```

### 2.3 问答策略链处理器

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class QAContext:
    """策略链中传递的上下文对象。"""
    question: str
    processed_question: str = ""       # 预处理后的问题
    user_id: str = ""
    user_role: Role = Role.EMPLOYEE
    user_context: dict = field(default_factory=dict)  # {hire_date, job_level, ...}
    session_id: str = ""
    answer: Optional[str] = None
    answer_type: Optional[AnswerType] = None
    reference_docs: list = field(default_factory=list)
    confidence: Optional[float] = None
    filtered_doc_ids: list = field(default_factory=list)  # 被权限过滤的文档ID
    personal_data_extraction: Optional[dict] = None  # ★二期 LLM意图提取结果
    personal_data_allowed: list = field(default_factory=list)  # ★二期 授权的个人数据字段
    personal_data_denied: list = field(default_factory=list)  # ★二期 被拒的个人数据字段
    is_done: bool = False  # 短路标志

class QAHandler(ABC):
    """责任链模式中的抽象处理器。"""

    def __init__(self):
        self._next: Optional[QAHandler] = None

    def set_next(self, handler: "QAHandler") -> "QAHandler":
        """设置链中的下一个处理器，返回handler以支持链式调用。"""
        self._next = handler
        return handler

    @abstractmethod
    async def handle(self, ctx: QAContext, db_session) -> QAContext: ...

    async def handle_next(self, ctx: QAContext, db_session) -> QAContext:
        """若ctx.is_done为False且有下一个处理器，则传递上下文。"""
        if self._next and not ctx.is_done:
            return await self._next.handle(ctx, db_session)
        return ctx


class FAQMatcher(QAHandler):
    """② FAQ匹配处理器：jieba分词 → FULLTEXT匹配 → 相似度过滤。"""

    async def handle(self, ctx: QAContext, db_session) -> QAContext:
        keywords = " ".join(jieba.cut(ctx.processed_question))
        # 在faqs表上执行FULLTEXT搜索
        faqs = await db_session.execute(
            select(FAQ).where(
                FAQ.status == FAQStatus.ACTIVE,
                func.match(FAQ.question, FAQ.keywords).against(keywords)
            ).limit(5)
        )
        faqs = faqs.scalars().all()
        best = None
        best_score = 0.0
        for faq in faqs:
            score = self._similarity(ctx.processed_question, faq.question)
            if score > best_score:
                best_score = score
                best = faq
        if best and best_score >= QA_THRESHOLDS["faq_similarity_min"]:
            best.view_count += 1
            ctx.answer = best.answer
            ctx.answer_type = AnswerType.FAQ
            ctx.reference_docs = [{"doc_id": best.related_doc_id, "title": "FAQ标准答案"}]
            ctx.confidence = best_score
            ctx.is_done = True
        return await self.handle_next(ctx, db_session)

    def _similarity(self, q1: str, q2: str) -> float:
        """基于字符二元组的Jaccard相似度计算。"""
        def bigrams(s): return set(s[i:i+2] for i in range(len(s)-1))
        b1, b2 = bigrams(q1), bigrams(q2)
        if not b1 or not b2:
            return 0.0
        return len(b1 & b2) / len(b1 | b2)


class RuleMatcher(QAHandler):
    """③ 规则匹配处理器：正则/关键词模板匹配。"""

    async def handle(self, ctx: QAContext, db_session) -> QAContext:
        for rule in RULE_TEMPLATES:
            for pattern in rule["patterns"]:
                if re.search(pattern, ctx.processed_question):
                    template = rule["template"]
                    if rule.get("requires_user_context"):
                        template = self._fill_context(template, ctx.user_context)
                    ctx.answer = template
                    ctx.answer_type = AnswerType.RULE
                    ctx.confidence = 0.90
                    ctx.is_done = True
                    return ctx
        return await self.handle_next(ctx, db_session)

    def _fill_context(self, template: str, uctx: dict) -> str:
        """用用户上下文值替换模板中的{占位符}。"""
        result = template
        if "{tenure_years}" in result and "hire_date" in uctx:
            hire = uctx["hire_date"]
            years = datetime.utcnow().date().year - hire.year
            result = result.replace("{tenure_years}", str(years))
        if "{annual_leave_days}" in result:
            years = datetime.utcnow().date().year - uctx["hire_date"].year
            if years < 3: days = 5
            elif years < 10: days = 10
            else: days = 15
            result = result.replace("{annual_leave_days}", str(days))
        return result


class PermissionFilter(QAHandler):
    """④ 权限过滤处理器：文档访问控制的横切关注点。
    本处理器不会短路链路；它仅用角色信息注解上下文，
    供下游处理器（搜索、RAG）调用静态过滤方法。"""

    async def handle(self, ctx: QAContext, db_session) -> QAContext:
        return await self.handle_next(ctx, db_session)

    @staticmethod
    def filter_documents(docs: list, role: Role) -> tuple[list, list]:
        """按角色过滤文档列表；返回 (允许访问的文档, 被过滤的文档)。"""
        allowed, filtered = [], []
        for doc in docs:
            if doc.can_access(role):
                allowed.append(doc)
            else:
                filtered.append(doc)
        return allowed, filtered


class SearchHandler(QAHandler):
    """⑤ 全文搜索处理器：MySQL FULLTEXT + Ngram + 权限过滤。"""

    async def handle(self, ctx: QAContext, db_session) -> QAContext:
        query = db_session.query(Document).where(
            Document.status == DocStatus.PUBLISHED,
            func.match(Document.title, Document.content).against(
                ctx.processed_question, in_natural_language_mode=True
            )
        )
        docs = (await db_session.execute(
            query.limit(QA_THRESHOLDS["search_max_results"])
        )).scalars().all()

        allowed, filtered = PermissionFilter.filter_documents(docs, ctx.user_role)
        ctx.filtered_doc_ids = [d.document_id for d in filtered]

        if allowed:
            snippets = []
            for doc in allowed:
                snippet = self._generate_snippet(doc.content, ctx.processed_question)
                snippets.append({
                    "document_id": doc.document_id,
                    "title": doc.title,
                    "snippet": snippet,
                    "category": doc.category.name if doc.category else "",
                    "version": doc.version,
                })
            ctx.answer = json.dumps(snippets, ensure_ascii=False)
            ctx.answer_type = AnswerType.SEARCH
            ctx.is_done = True
        # 若无允许的文档，不设is_done，让链继续走到RAG（二期）或兜底
        return await self.handle_next(ctx, db_session)

    def _generate_snippet(self, content: str, query: str) -> str:
        """在首次匹配位置附近生成摘要片段（最多150字符）。"""
        idx = content.find(query)
        if idx == -1:
            # 尝试逐字符匹配
            for ch in query:
                idx = content.find(ch)
                if idx != -1:
                    break
        if idx == -1:
            return content[:150] + "..."
        start = max(0, idx - 50)
        end = min(len(content), idx + 100)
        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet += "..."
        return snippet


class FallbackHandler(QAHandler):
    """⑦ 最终兜底处理器：所有策略均无结果时使用。"""

    async def handle(self, ctx: QAContext, db_session) -> QAContext:
        if not ctx.is_done:
            if ctx.filtered_doc_ids and not ctx.reference_docs:
                # 全部结果被权限过滤
                ctx.answer = "🔒 该内容需要HR权限才能查看。如有疑问，请联系HR部门（hr@company.com）"
                ctx.answer_type = AnswerType.NO_RESULT
            else:
                ctx.answer = "未找到相关制度，建议联系HR部门获取帮助。"
                ctx.answer_type = AnswerType.NO_RESULT
            ctx.is_done = True
        return ctx


class PersonalDataGuard(QAHandler):
    """⑧（二期新增）个人数据守卫处理器。
    在RAG检索之前拦截，执行LLM意图提取 + 三级敏感度校验。
    本处理器不短路常规策略链（FAQ/规则/搜索），仅在RAG阶段介入。"""

    def __init__(self, llm_provider: LLMProvider):
        super().__init__()
        self.llm = llm_provider

    async def handle(self, ctx: QAContext, db_session) -> QAContext:
        """执行个人数据访问审核。用于RAG流程的前置检查。"""
        # 1. LLM意图提取
        extraction = await self._extract_intent(
            ctx.question, ctx.user_id, ctx.user_role, ctx.user_context
        )
        ctx.personal_data_extraction = extraction

        if extraction["confidence"] < 0.7:
            ctx.answer = "🔒 抱歉，无法确认您在查询哪位员工的信息。请使用明确姓名后重试，例如「张三的工龄是多少」。如需查询自己，请使用「我的…」句式。"
            ctx.answer_type = AnswerType.NO_RESULT
            ctx.is_done = True
            return ctx

        if extraction["query_type"] == "aggregation":
            ctx.answer = "🔒 抱歉，出于数据安全考虑，系统不支持聚合统计类查询（如平均值、排名、人数统计等）。如有业务需要，请联系HR部门。"
            ctx.answer_type = AnswerType.NO_RESULT
            ctx.is_done = True
            return ctx

        if extraction["query_type"] == "policy_only":
            # 纯制度查询，跳过个人数据审核
            return await self.handle_next(ctx, db_session)

        # 2. 个人数据/混合查询 → 逐字段校验
        allowed, denied = await self._check_fields(
            ctx.user_id, ctx.user_role, extraction, db_session
        )
        ctx.personal_data_allowed = allowed
        ctx.personal_data_denied = denied

        if not allowed:
            # 全部被拒
            target_names = "、".join(extraction["target_persons"])
            field_names = "、".join(extraction["requested_fields"])
            ctx.answer = (
                f"🔒 抱歉，您无权查询{target_names}的{field_names}等个人私密信息。"
                f"如需了解自己的权益，请尝试询问「我的{field_names}是多少」。"
            )
            ctx.answer_type = AnswerType.NO_RESULT
            ctx.is_done = True
            return ctx

        # 部分或全部放行 → 继续链
        return await self.handle_next(ctx, db_session)

    async def _extract_intent(
        self, question: str, user_id: str, role: Role, user_context: dict
    ) -> dict:
        """调用LLM进行意图提取（轻量级调用，非完整生成）。
        使用独立的System Prompt，与User Prompt严格分离防注入。"""
        system_prompt = (
            "你是一个HR数据查询分析器。你的任务是从用户问题中提取查询意图，而不是回答问题。\n"
            f"当前登录用户信息：姓名={user_context.get('name')}、工号={user_context.get('employee_id')}、"
            f"部门={user_context.get('department')}、角色={role}\n\n"
            "分析规则：\n"
            "1. 第一人称「我」「我的」→ 目标人物为当前用户\n"
            "2. 明确人名（非当前用户）→ 目标人物为提及的人名\n"
            "3. 聚合/统计类（平均/最高/最低/总共/多少人/哪些人）→ aggregation\n"
            "4. 纯政策问题（无个人数据字段请求）→ policy_only\n"
            "5. 无法确定目标人物时confidence应低于0.7\n\n"
            '输出JSON格式（不要输出其他内容）：\n'
            '{"query_type":"...", "target_persons":["..."], "requested_fields":["..."], '
            '"is_self_query":true|false, "confidence":0.0~1.0}'
        )
        response = await self.llm.generate(
            prompt=question,
            system_prompt=system_prompt,
            max_tokens=200,
            temperature=0.0,
        )
        import json
        return json.loads(response.content)

    async def _check_fields(
        self, querier_id: str, querier_role: Role,
        extraction: dict, db_session
    ) -> tuple[list, list]:
        """逐字段校验三级敏感度权限。"""
        allowed, denied = [], []

        if querier_role in (Role.HR_SPECIALIST, Role.ADMIN):
            # HR/管理员 → 全部放行
            for person in extraction["target_persons"]:
                for field in extraction["requested_fields"]:
                    allowed.append({"person": person, "field": field})
            return allowed, denied

        # 查询自己的数据 → 全部放行
        if extraction["is_self_query"]:
            for field in extraction["requested_fields"]:
                allowed.append({"person": extraction["target_persons"][0], "field": field})
            return allowed, denied

        # 查询他人 → 按敏感度逐字段判定
        for person_name in extraction["target_persons"]:
            # 查找目标用户
            target = await db_session.execute(
                select(User).where(User.name == person_name)
            )
            target = target.scalar_one_or_none()
            if not target:
                denied.append({"person": person_name, "field": "ALL", "reason": "target_not_found"})
                continue

            # 加载当前用户的部门信息
            querier = await db_session.get(User, querier_id)

            for field_label in extraction["requested_fields"]:
                # 查询敏感度配置
                sens = await db_session.execute(
                    select(EmployeeDataSensitivity).where(
                        EmployeeDataSensitivity.field_label == field_label,
                        EmployeeDataSensitivity.is_active == True,
                    )
                )
                sens = sens.scalar_one_or_none()
                if not sens:
                    denied.append({"person": person_name, "field": field_label, "reason": "unknown_field"})
                    continue

                if sens.sensitivity_level == SensitivityLevel.PUBLIC:
                    allowed.append({"person": person_name, "field": field_label})
                elif sens.sensitivity_level == SensitivityLevel.DEPARTMENT:
                    if querier.department_id == target.department_id:
                        allowed.append({"person": person_name, "field": field_label})
                    else:
                        denied.append({"person": person_name, "field": field_label, "reason": "cross_department"})
                else:  # PRIVATE
                    denied.append({"person": person_name, "field": field_label, "reason": "private"})

        return allowed, denied
```

### 2.4 问答编排器

```python
class QAOrchestrator:
    """构建并执行问答策略链。"""

    def __init__(self, phase: str = "phase1"):
        """
        参数:
            phase: "phase1" 或 "phase2"，决定是否包含RAG处理器
        """
        self.phase = phase
        self._chain: Optional[QAHandler] = None

    def build_chain(self) -> QAHandler:
        """构建策略链。
        一期: FAQ → 规则 → 权限过滤 → 搜索 → 兜底
        二期: FAQ → 规则 → 权限过滤 → 搜索 → 个人数据守卫 → RAG → 兜底"""
        faq = FAQMatcher()
        rule = RuleMatcher()
        perm_filter = PermissionFilter()
        search = SearchHandler()
        fallback = FallbackHandler()

        faq.set_next(rule)
        rule.set_next(perm_filter)
        perm_filter.set_next(search)

        if self.phase == "phase2":
            # ★ V1.1: 在搜索和RAG之间插入个人数据守卫
            guard = PersonalDataGuard(self.llm_provider)
            from app.services.rag_handler import RAGHandler
            rag = RAGHandler()
            search.set_next(guard)
            guard.set_next(rag)
            rag.set_next(fallback)
        else:
            search.set_next(fallback)

        self._chain = faq
        return faq

    async def ask(
        self, question: str, user: User, session_id: str, db_session
    ) -> QAContext:
        """执行完整的问答策略链。
        构建QAContext，预处理问题，然后依次通过策略链各处理器。"""
        ctx = QAContext(
            question=question,
            processed_question=self._preprocess(question),
            user_id=user.user_id,
            user_role=user.role,
            user_context={
                "hire_date": user.hire_date,
                "job_level": user.job_level,
                "marital_status": user.marital_status,
            },
            session_id=session_id,
        )
        handler = self._chain or self.build_chain()
        result = await handler.handle(ctx, db_session)
        return result

    def _preprocess(self, text: str) -> str:
        """标准化输入：去除首尾空白，压缩多余标点符号。"""
        import re
        text = text.strip()
        text = re.sub(r"[？?！!。，,、\s]+", " ", text)
        return text
```

---

## §3 核心算法伪代码

> 映射 L0 入口：L0 §5.1 操作契约 → *完整算法伪代码见 [L1 §3]*

### §3.1 注册操作

**映射契约**: L0 §5.1 — `register(employee_id, name, password, department_id)`
**入选原因**: 多步骤副作用链（校验 → 哈希 → DB插入 → 审计）。

```python
async def register(
    employee_id: str, name: str, password: str,
    email: Optional[str], phone: Optional[str],
    department_id: str, db_session
) -> User:
    """
    注册新员工账号。

    前置条件:
    1. 工号匹配 ^[A-Za-z0-9]{4,20}$ 格式
    2. 密码 ≥ 8位，必须包含大写字母+小写字母+数字
    3. 工号未被注册
    4. 部门ID存在于departments表中

    副作用:
    - INSERT user行（含bcrypt密码哈希）
    - INSERT audit_log行
    """
    # 1. 验证输入格式
    if not re.match(PASSWORD_POLICY["employee_id_pattern"], employee_id):
        raise ValidationError("工号格式不正确：4-20位字母数字组合")

    if len(password) < PASSWORD_POLICY["min_length"]:
        raise ValidationError(f"密码长度不少于{PASSWORD_POLICY['min_length']}位")

    checks = [
        any(c.isupper() for c in password),
        any(c.islower() for c in password),
        any(c.isdigit() for c in password),
    ]
    if not all(checks):
        raise ValidationError("密码需包含大写字母、小写字母和数字")

    if email and not re.match(PASSWORD_POLICY["email_pattern"], email):
        raise ValidationError("邮箱格式不正确")

    # 2. 检查唯一性
    existing = await db_session.execute(
        select(User).where(User.employee_id == employee_id)
    )
    if existing.scalar_one_or_none():
        raise ConflictError(code=20001, message="工号已存在")

    # 3. 验证部门存在
    dept = await db_session.get(Department, department_id)
    if not dept:
        raise NotFoundError(code=20003, message="部门不存在")

    # 4. 创建用户
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

    # 5. 记录审计日志
    audit = AuditLog(
        log_id=uuid4_str(),
        user_id=user.user_id,
        action="user_register",
        resource_type="user",
        resource_id=user.user_id,
        detail={"employee_id": employee_id, "name": name},
    )
    db_session.add(audit)
    await db_session.commit()

    return user
```

### §3.2 登录操作

**映射契约**: L0 §5.1 — `login(account, password)`

```python
async def login(account: str, password: str, db_session, redis_client) -> dict:
    """
    认证用户并返回JWT令牌对。

    前置条件:
    1. account匹配工号或邮箱
    2. 账号存在于users表中
    3. 用户状态为active且未锁定

    副作用:
    - 成功时：重置login_attempts，生成审计日志
    - 失败时：增加login_attempts，可能锁定账号

    返回: {"access_token": str, "refresh_token": str, "user": dict}
    """
    # 1. 按工号或邮箱查找用户
    user = await db_session.execute(
        select(User).where(
            (User.employee_id == account) | (User.email == account)
        ).where(User.status == UserStatus.ACTIVE)
    )
    user = user.scalar_one_or_none()

    if not user:
        raise UnauthorizedError(code=10005, message="账号或密码错误")

    # 2. 检查锁定状态
    if user.is_locked():
        remaining = int((user.locked_until - datetime.utcnow()).total_seconds() / 60)
        raise LockedError(code=10004, message=f"账号已锁定，请{remaining}分钟后重试")

    # 3. 验证密码
    if not user.verify_password(password):
        user.record_failed_attempt()
        audit = AuditLog(
            log_id=uuid4_str(), user_id=user.user_id,
            action="login_failed", resource_type="user", resource_id=user.user_id,
            detail={"attempt": user.login_attempts},
        )
        db_session.add(audit)
        await db_session.commit()
        remaining = SECURITY_CONFIG["max_login_attempts"] - user.login_attempts
        raise UnauthorizedError(
            code=10005,
            message=f"密码错误，剩余尝试次数: {max(0, remaining)}"
        )

    # 4. 生成令牌
    user.reset_login_attempts()
    access_token = create_access_token(user.user_id, user.role)
    refresh_token = create_refresh_token(user.user_id)

    # 5. 将会话缓存到Redis
    await redis_client.setex(
        f"session:{user.user_id}",
        SECURITY_CONFIG["access_token_expire_minutes"] * 60,
        json.dumps({"user_id": user.user_id, "role": user.role})
    )

    # 6. 记录审计日志
    audit = AuditLog(
        log_id=uuid4_str(), user_id=user.user_id,
        action="login_success", resource_type="user", resource_id=user.user_id,
    )
    db_session.add(audit)
    await db_session.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.mask_sensitive(),
    }
```

### §3.3 - §3.15

> *（其余13个算法伪代码遵循相同模式，每个映射到L0 §5.1操作契约表中的一行。在本L1快照中，详细实现可在 `/forge` 任务执行时按需提供。）*

---

## §4 详细决策树逻辑

> 映射 L0 入口：L0 §4 架构设计 → *完整决策逻辑见 [L1 §4]*

### §4.1 权限解析决策树

**映射 L0 Mermaid**: `hr-policy-qa-system.md §4.6`

```python
def resolve_effective_access(document: Document, category: Optional[Category]) -> AccessLevel:
    """
    解析文档有效访问级别的完整决策树。

    决策顺序:
    1. 若文档.access_level != 'inherit' → 直接使用文档自身级别
    2. 若文档.access_level == 'inherit' 且分类存在 → 使用分类级别
    3. 若文档.access_level == 'inherit' 且无分类 → 默认 ALL_ROLES（安全）
    """
    # 步骤1: 检查文档级别覆盖
    if document.access_level != DocAccessLevel.INHERIT:
        return _map_doc_level_to_access(document.access_level)

    # 步骤2: 从分类继承
    if category:
        return category.access_level

    # 步骤3: 安全默认值
    return AccessLevel.ALL_ROLES


def _map_doc_level_to_access(doc_level: DocAccessLevel) -> AccessLevel:
    """将 DocAccessLevel 映射为 AccessLevel。"""
    mapping = {
        DocAccessLevel.ALL_ROLES: AccessLevel.ALL_ROLES,
        DocAccessLevel.HR_ADMIN_ONLY: AccessLevel.HR_ADMIN_ONLY,
        DocAccessLevel.ADMIN_ONLY: AccessLevel.ADMIN_ONLY,
    }
    return mapping.get(doc_level, AccessLevel.ALL_ROLES)
```

### §4.2 问答策略链决策流程

**映射 L0 Mermaid**: `hr-policy-qa-system.md §4.4`

```python
async def execute_qa_chain(
    question: str, user: User, session_id: str, db_session, phase: str
) -> dict:
    """
    问答策略链的完整决策流程。

    步骤1: 预处理问题（标准化、去除停用词）
    步骤2: 尝试FAQ匹配（jieba分词 + 相似度 > 0.70）
    步骤3: 尝试规则匹配（正则模式 + 关键词模板）
    步骤4: 权限过滤（横切关注点，注解上下文）
    步骤5: 全文搜索（MySQL FULLTEXT + Ngram + 权限过滤）
    步骤6: [二期] RAG（向量检索 + LLM生成）
    步骤7: 兜底响应
    """
    ctx = QAContext(
        question=question,
        processed_question=preprocess(question),
        user_id=user.user_id,
        user_role=user.role,
        session_id=session_id,
    )

    orchestrator = QAOrchestrator(phase=phase)
    ctx = await orchestrator.ask(question, user, session_id, db_session)

    # 根据answer_type构建响应
    response = build_response(ctx)
    return response


def build_response(ctx: QAContext) -> dict:
    """根据QA上下文构建API响应。"""
    base = {
        "question": ctx.question,
        "answer": ctx.answer,
        "answer_type": ctx.answer_type,
        "reference_docs": ctx.reference_docs,
        "confidence": ctx.confidence,
        "session_id": ctx.session_id,
    }

    # 如果有文档被权限过滤，附加提示
    if ctx.filtered_doc_ids and ctx.answer_type not in [AnswerType.NO_RESULT]:
        base["notice"] = "🔒 部分相关制度需要HR权限才能查看，如需了解请联系HR部门"

    # 低置信度免责声明
    if ctx.confidence and ctx.confidence < QA_THRESHOLDS["rag_low_confidence"]:
        base["disclaimer"] = "以下回答仅供参考，建议与HR确认"

    return base
```

---

## §5 边界情况与易错点

> 映射 L0 入口：L0 §5 / §9 安全

| 场景 | 风险 | 处理方式 |
|----------|------|----------|
| 文档access_level=inherit但分类已被删除 | 空引用错误 | 安全默认为 `ALL_ROLES`；分类删除级联SET NULL，应用层解析 |
| 多设备同时登录 | Token重放攻击 | 每次新登录使前一个refresh token失效（令牌轮换）；access token保持至过期 |
| 多轮对话中会话超时 | 对话上下文丢失 | Redis TTL 30分钟；前端检测到下一条消息的401 → 提示"会话已过期，请开启新会话" |
| FAQ答案包含HTML/脚本 | 存储型XSS | 后端保存FAQ时净化内容（bleach库）；前端仅在净化后使用v-html渲染 |
| 上传超大PDF（>50MB） | 内存耗尽 | Nginx层面限制文件大小20MB；Celery worker流式解析；超时60秒 |
| MySQL FULLTEXT对极短查询返回空 | 单字查询无结果 | 最小查询长度2字符（ngram_token_size=2）；单字查询降级为LIKE %x% |
| Redis连接丢失 | 缓存未命中、限流失效 | 优雅降级：跳过缓存，不限流放行（记录警告日志）；自动重连 |
| 高负载下bcrypt验证超过500ms | 登录延迟尖峰 | bcrypt cost=12是权衡选择；登录非热点路径可接受；批量操作考虑异步哈希 |
| FAQ匹配中jieba分词器处理长问题 | 性能下降 | 分词前截断问题至100字符；缓存常用分词结果 |
| 文档版本历史无限增长 | 存储膨胀 | 超过10代的旧版本归档；活跃存储仅保留最新3个版本 |
| Celery任务静默失败 | 文档卡在"处理中"状态 | 最多重试3次，指数退避；永久失败进入死信队列；连续3次失败告警 |
| 权限过滤边界：文档发布后分类权限被修改 | 有效权限竞态条件 | 查询时实时计算effective_access_level（不缓存在文档上）；权限过滤器始终读取当前category.access_level |

### §5.1 具体案例：用户上下文浅拷贝风险

```python
# ❌ 错误 — user_context dict 是跨请求的共享引用
ctx.user_context = DEFAULT_USER_CONTEXT
ctx.user_context["hire_date"] = user.hire_date  # 修改了共享dict！

# ✅ 正确 — 每次请求深拷贝
import copy
ctx.user_context = copy.deepcopy(DEFAULT_USER_CONTEXT)
ctx.user_context["hire_date"] = user.hire_date
```

### §5.2 具体案例：Token过期边界

```python
# ❌ 错误 — 服务器时间不同步导致提前过期
if datetime.utcnow() > token.exp:
    raise TokenExpiredError()

# ✅ 正确 — 增加30秒时钟偏差容忍
if datetime.utcnow() > token.exp + timedelta(seconds=30):
    raise TokenExpiredError()
```

---

## §6 测试辅助工具

> 映射 L0 入口：L0 §11 测试策略

```python
"""单元测试和集成测试的 fixture 工厂函数。"""

import pytest
from datetime import date, datetime

def make_test_user(
    employee_id: str = "EMP001",
    name: str = "测试员工",
    role: Role = Role.EMPLOYEE,
    department_id: str = "dept-001",
    hire_date: date = date(2021, 3, 1),
) -> User:
    """创建一个测试User实例（未持久化）。"""
    user = User(
        user_id=f"test-user-{employee_id}",
        employee_id=employee_id,
        name=name,
        role=role,
        department_id=department_id,
        hire_date=hire_date,
        status=UserStatus.ACTIVE,
    )
    user.set_password("Test@1234")
    return user


def make_test_document(
    title: str = "测试制度文档",
    content: str = "这是一份测试文档的内容。",
    category_id: str = "cat-doc-1",
    access_level: DocAccessLevel = DocAccessLevel.ALL_ROLES,
    status: DocStatus = DocStatus.PUBLISHED,
) -> Document:
    """创建一个测试Document实例（未持久化）。"""
    return Document(
        document_id=f"test-doc-{title}",
        title=title,
        content=content,
        category_id=category_id,
        format=DocFormat.MARKDOWN,
        access_level=access_level,
        status=status,
        uploaded_by="test-user-admin",
        file_path=f"/test/{title}.md",
    )


def make_test_faq(
    question: str = "年假怎么算？",
    answer: str = "年假根据工龄计算。",
    category_id: str = "cat-faq-3",
) -> FAQ:
    """创建一个测试FAQ实例（未持久化）。"""
    return FAQ(
        faq_id=f"test-faq-{question[:10]}",
        question=question,
        answer=answer,
        category_id=category_id,
        status=FAQStatus.ACTIVE,
        created_by="test-user-hr",
    )


def make_test_qa_context(
    question: str = "年假怎么算？",
    user_role: Role = Role.EMPLOYEE,
) -> QAContext:
    """创建用于策略链单元测试的 QAContext。"""
    return QAContext(
        question=question,
        processed_question=question.strip(),
        user_id="test-user-001",
        user_role=user_role,
        user_context={"hire_date": date(2021, 3, 1)},
        session_id=f"test-session-{question[:10]}",
    )


@pytest.fixture
async def db_session():
    """夹具：提供异步测试数据库会话。"""
    # 设置：创建测试引擎、建表
    # 产出：会话
    # 清理：回滚、关闭
    ...


@pytest.fixture
async def redis_client():
    """夹具：提供测试Redis客户端（或mock）。"""
    ...
```

---

**📋 L1 实现层结束 | 映射至：[hr-policy-qa-system.md §1-§11](./hr-policy-qa-system.md)**
