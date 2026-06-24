"""常量配置 — 权限矩阵、安全常量、阈值、规则模板库"""

from app.enums.enums import (
    Role, AccessLevel, DocAccessLevel, SensitivityLevel,
)


# ── 权限矩阵（配置表）──
PERMISSION_MATRIX = {
    (AccessLevel.ALL_ROLES, Role.EMPLOYEE): True,
    (AccessLevel.ALL_ROLES, Role.HR_SPECIALIST): True,
    (AccessLevel.ALL_ROLES, Role.ADMIN): True,
    (AccessLevel.HR_ADMIN_ONLY, Role.EMPLOYEE): False,
    (AccessLevel.HR_ADMIN_ONLY, Role.HR_SPECIALIST): True,
    (AccessLevel.HR_ADMIN_ONLY, Role.ADMIN): True,
    (AccessLevel.ADMIN_ONLY, Role.EMPLOYEE): False,
    (AccessLevel.ADMIN_ONLY, Role.HR_SPECIALIST): False,
    (AccessLevel.ADMIN_ONLY, Role.ADMIN): True,
}

# ── DocAccessLevel → AccessLevel 映射 ──
DOC_TO_ACCESS_MAP = {
    DocAccessLevel.ALL_ROLES: AccessLevel.ALL_ROLES,
    DocAccessLevel.HR_ADMIN_ONLY: AccessLevel.HR_ADMIN_ONLY,
    DocAccessLevel.ADMIN_ONLY: AccessLevel.ADMIN_ONLY,
}

# ── 安全与限流常量 ──
SECURITY_CONFIG = {
    "bcrypt_rounds": 12,
    "access_token_expire_minutes": 120,
    "refresh_token_expire_days": 7,
    "max_login_attempts": 5,
    "lockout_duration_minutes": 30,
    "session_idle_timeout_minutes": 30,
    "max_dialogue_rounds": 20,
    "rate_limit_qna_per_minute": 20,
    "rate_limit_search_per_minute": 30,
}

PASSWORD_POLICY = {
    "min_length": 8,
    "require_uppercase": True,
    "require_lowercase": True,
    "require_digit": True,
    "employee_id_pattern": r"^[A-Za-z0-9]{4,20}$",
    "phone_pattern": r"^1[3-9]\d{9}$",
    "email_pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
}

# ── 问答策略链阈值 ──
QA_THRESHOLDS = {
    "faq_similarity_min": 0.70,
    "search_max_results": 20,
    "rag_top_k_retrieval": 10,
    "rag_top_n_prompt": 5,
    "rag_chunk_token_size": 500,
    "rag_high_confidence": 0.85,
    "rag_low_confidence": 0.70,
    "llm_timeout_seconds": 5,
    "llm_circuit_breaker_failures": 5,
    "llm_circuit_breaker_timeout": 30,
}

# ── 规则模板库（一期）──
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
        "requires_user_context": True,
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

# ── 默认用户上下文 ──
DEFAULT_USER_CONTEXT = {
    "hire_date": None,
    "job_level": None,
    "marital_status": None,
    "name": "",
    "employee_id": "",
    "department": "",
}
