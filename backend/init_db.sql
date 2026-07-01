-- ============================================================
-- HR制度智能问答系统 — 数据库初始化脚本
-- 数据库: hr_policy_qa
-- 字符集: utf8mb4 / utf8mb4_unicode_ci
-- MySQL: 8.0+
-- 说明: 此脚本在 MySQL 容器首次启动时自动执行
--       （挂载到 /docker-entrypoint-initdb.d/）
-- ============================================================

-- ════════════════════════════════════════════════════════════
-- 一、创建数据库（如不存在）
-- ════════════════════════════════════════════════════════════
-- 注：docker-compose 已通过 MYSQL_DATABASE 环境变量创建数据库，
--     此处仅作兜底。如需手动运行，请取消下面注释。
-- CREATE DATABASE IF NOT EXISTS hr_policy_qa
--     CHARACTER SET utf8mb4
--     COLLATE utf8mb4_unicode_ci;
-- USE hr_policy_qa;

-- ════════════════════════════════════════════════════════════
-- 二、数据表定义
-- ════════════════════════════════════════════════════════════

-- -----------------------------------------------------------
-- 2.1 部门表 departments
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS departments (
    department_id   VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '部门ID(UUID hex)',
    name            VARCHAR(100)  NOT NULL COMMENT '部门名称',
    parent_id       VARCHAR(64)   DEFAULT NULL COMMENT '上级部门ID(树形结构)',
    sort_order      INT           NOT NULL DEFAULT 0 COMMENT '排序号',

    INDEX idx_parent_id (parent_id),
    CONSTRAINT fk_department_parent
        FOREIGN KEY (parent_id) REFERENCES departments(department_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='部门表(树形结构)';

-- -----------------------------------------------------------
-- 2.2 用户表 users
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id         VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '用户ID(UUID hex)',
    employee_id     VARCHAR(20)   NOT NULL COMMENT '工号',
    name            VARCHAR(50)   NOT NULL COMMENT '姓名',
    email           VARCHAR(100)  DEFAULT NULL COMMENT '邮箱',
    phone           VARCHAR(15)   DEFAULT NULL COMMENT '手机号',
    password_hash   VARCHAR(255)  NOT NULL COMMENT 'bcrypt密码哈希',
    role            ENUM('employee','hr_specialist','admin')
                                  NOT NULL DEFAULT 'employee' COMMENT '角色',
    department_id   VARCHAR(64)   NOT NULL COMMENT '所属部门ID',
    job_level       VARCHAR(20)   DEFAULT NULL COMMENT '职级(如P5/P6/M1/M2)',
    hire_date       DATE          NOT NULL COMMENT '入职日期',
    work_location   VARCHAR(50)   DEFAULT NULL COMMENT '工作地',
    marital_status  ENUM('single','married')
                                  DEFAULT NULL COMMENT '婚姻状态',
    status          ENUM('active','disabled')
                                  NOT NULL DEFAULT 'active' COMMENT '账号状态',
    login_attempts  INT           NOT NULL DEFAULT 0 COMMENT '连续登录失败次数',
    locked_until    DATETIME      DEFAULT NULL COMMENT '锁定截止时间',
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    UNIQUE INDEX idx_employee_id (employee_id),
    INDEX idx_email (email),
    INDEX idx_department_id (department_id),
    INDEX idx_status (status),

    CONSTRAINT fk_user_department
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='用户表';

-- -----------------------------------------------------------
-- 2.3 分类标签表 categories
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    category_id     VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '分类ID(UUID hex)',
    name            VARCHAR(100)  NOT NULL COMMENT '分类名称',
    parent_id       VARCHAR(64)   DEFAULT NULL COMMENT '上级分类ID',
    type            ENUM('document','faq')
                                  NOT NULL COMMENT '分类类型',
    access_level    ENUM('all_roles','hr_admin_only','admin_only')
                                  NOT NULL DEFAULT 'all_roles' COMMENT '默认检索权限级别',
    sort_order      INT           NOT NULL DEFAULT 0 COMMENT '排序号',

    INDEX idx_parent_id (parent_id),
    INDEX idx_type (type),

    CONSTRAINT fk_category_parent
        FOREIGN KEY (parent_id) REFERENCES categories(category_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='分类标签表';

-- -----------------------------------------------------------
-- 2.4 制度文档表 documents
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS documents (
    document_id     VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '文档ID(UUID hex)',
    title           VARCHAR(200)  NOT NULL COMMENT '文档标题',
    content         LONGTEXT      NOT NULL COMMENT '解析后的文本内容',
    category_id     VARCHAR(64)   NOT NULL COMMENT '分类ID',
    format          ENUM('pdf','word','markdown','html')
                                  NOT NULL COMMENT '原始格式',
    version         VARCHAR(10)   NOT NULL DEFAULT '1.0' COMMENT '版本号',
    version_note    VARCHAR(500)  DEFAULT NULL COMMENT '版本变更说明',
    status          ENUM('draft','published','archived')
                                  NOT NULL DEFAULT 'draft' COMMENT '文档状态',
    access_level    ENUM('inherit','all_roles','hr_admin_only','admin_only')
                                  NOT NULL DEFAULT 'inherit' COMMENT '检索权限级别',
    uploaded_by     VARCHAR(64)   NOT NULL COMMENT '上传者用户ID',
    file_path       VARCHAR(500)  NOT NULL COMMENT '原始文件存储路径',
    word_count      INT           NOT NULL DEFAULT 0 COMMENT '字数统计',
    chunk_count     INT           NOT NULL DEFAULT 0 COMMENT '分块数量',
    embedding_status VARCHAR(20)  NOT NULL DEFAULT 'pending' COMMENT '向量化状态',
    published_at    DATETIME      DEFAULT NULL COMMENT '发布时间',
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_category_id (category_id),
    INDEX idx_status (status),
    INDEX idx_embedding_status (embedding_status),
    INDEX idx_uploaded_by (uploaded_by),
    FULLTEXT INDEX ft_document_content (title, content) WITH PARSER ngram,

    CONSTRAINT fk_document_category
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_document_uploader
        FOREIGN KEY (uploaded_by) REFERENCES users(user_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='制度文档表';

-- -----------------------------------------------------------
-- 2.5 文档版本表 document_versions
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS document_versions (
    version_id      VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '版本ID(UUID hex)',
    document_id     VARCHAR(64)   NOT NULL COMMENT '所属文档ID',
    version         VARCHAR(10)   NOT NULL COMMENT '版本号',
    content_snapshot LONGTEXT     NOT NULL COMMENT '内容快照',
    change_summary  VARCHAR(1000) DEFAULT NULL COMMENT '变更摘要',
    changed_by      VARCHAR(64)   NOT NULL COMMENT '修改者用户ID',
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    INDEX idx_document_id (document_id),
    INDEX idx_changed_by (changed_by),

    CONSTRAINT fk_version_document
        FOREIGN KEY (document_id) REFERENCES documents(document_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_version_changer
        FOREIGN KEY (changed_by) REFERENCES users(user_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='文档版本快照表';

-- -----------------------------------------------------------
-- 2.6 文档分块表 document_chunks
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS document_chunks (
    chunk_id        VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '分块ID(UUID hex)',
    document_id     VARCHAR(64)   NOT NULL COMMENT '所属文档ID',
    chunk_index     INT           NOT NULL COMMENT '分块序号',
    content         LONGTEXT      NOT NULL COMMENT '分块文本内容',
    token_count     INT           NOT NULL DEFAULT 0 COMMENT 'Token数量',
    embedding_status VARCHAR(20)  NOT NULL DEFAULT 'pending' COMMENT '向量化状态',
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    INDEX idx_document_id (document_id),
    INDEX idx_embedding_status (embedding_status),

    CONSTRAINT fk_chunk_document
        FOREIGN KEY (document_id) REFERENCES documents(document_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='文档分块表(向量化前)';

-- -----------------------------------------------------------
-- 2.7 FAQ表 faqs
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS faqs (
    faq_id          VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT 'FAQ ID(UUID hex)',
    question        VARCHAR(500)  NOT NULL COMMENT '问题',
    answer          LONGTEXT      NOT NULL COMMENT '答案',
    category_id     VARCHAR(64)   NOT NULL COMMENT '分类ID',
    related_doc_id  VARCHAR(64)   DEFAULT NULL COMMENT '关联文档ID',
    keywords        VARCHAR(500)  DEFAULT NULL COMMENT '关键词(逗号分隔)',
    view_count      INT           NOT NULL DEFAULT 0 COMMENT '浏览次数',
    status          ENUM('active','archived')
                                  NOT NULL DEFAULT 'active' COMMENT '状态',
    created_by      VARCHAR(64)   NOT NULL COMMENT '创建者用户ID',
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_category_id (category_id),
    INDEX idx_related_doc_id (related_doc_id),
    INDEX idx_status (status),
    INDEX idx_created_by (created_by),
    FULLTEXT INDEX ft_faq_question_answer (question, answer) WITH PARSER ngram,

    CONSTRAINT fk_faq_category
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_faq_document
        FOREIGN KEY (related_doc_id) REFERENCES documents(document_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_faq_creator
        FOREIGN KEY (created_by) REFERENCES users(user_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='FAQ问答表';

-- -----------------------------------------------------------
-- 2.8 问答记录表 qa_records
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS qa_records (
    record_id       VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '记录ID(UUID hex)',
    user_id         VARCHAR(64)   NOT NULL COMMENT '用户ID',
    session_id      VARCHAR(64)   NOT NULL COMMENT '会话ID',
    question        LONGTEXT      NOT NULL COMMENT '用户问题',
    answer          LONGTEXT      NOT NULL COMMENT '系统回答',
    answer_type     ENUM('faq','rule','search','rag','no_result')
                                  NOT NULL COMMENT '回答类型',
    confidence      FLOAT         DEFAULT NULL COMMENT '置信度(0-1)',
    reference_docs  JSON          DEFAULT NULL COMMENT '引用的文档列表',
    response_time_ms INT          NOT NULL DEFAULT 0 COMMENT '响应时间(毫秒)',
    feedback        ENUM('helpful','not_helpful')
                                  DEFAULT NULL COMMENT '用户反馈',
    feedback_reason VARCHAR(500)  DEFAULT NULL COMMENT '反馈原因',
    is_favorite     TINYINT(1)    NOT NULL DEFAULT 0 COMMENT '是否收藏',
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_created_at (created_at),
    INDEX idx_feedback (feedback),

    CONSTRAINT fk_qa_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='问答记录表';

-- -----------------------------------------------------------
-- 2.9 会话表 chat_sessions
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id      VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '会话ID(UUID hex)',
    user_id         VARCHAR(64)   NOT NULL COMMENT '用户ID',
    title           VARCHAR(200)  DEFAULT NULL COMMENT '会话标题',
    is_pinned       TINYINT(1)    NOT NULL DEFAULT 0 COMMENT '是否置顶',
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_user_id (user_id),

    CONSTRAINT fk_session_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='聊天会话表';

-- -----------------------------------------------------------
-- 2.10 纠错申请表 correction_requests
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS correction_requests (
    request_id      VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '申请ID(UUID hex)',
    document_id     VARCHAR(64)   NOT NULL COMMENT '目标文档ID',
    section         VARCHAR(500)  NOT NULL COMMENT '纠错章节/位置',
    description     LONGTEXT      NOT NULL COMMENT '纠错描述',
    submitted_by    VARCHAR(64)   NOT NULL COMMENT '提交者用户ID',
    reviewed_by     VARCHAR(64)   DEFAULT NULL COMMENT '审核者用户ID',
    status          ENUM('pending','approved','rejected')
                                  NOT NULL DEFAULT 'pending' COMMENT '审核状态',
    review_comment  VARCHAR(500)  DEFAULT NULL COMMENT '审核意见',
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
    reviewed_at     DATETIME      DEFAULT NULL COMMENT '审核时间',

    INDEX idx_document_id (document_id),
    INDEX idx_submitted_by (submitted_by),
    INDEX idx_reviewed_by (reviewed_by),
    INDEX idx_status (status),

    CONSTRAINT fk_correction_document
        FOREIGN KEY (document_id) REFERENCES documents(document_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_correction_submitter
        FOREIGN KEY (submitted_by) REFERENCES users(user_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_correction_reviewer
        FOREIGN KEY (reviewed_by) REFERENCES users(user_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='文档纠错申请表';

-- -----------------------------------------------------------
-- 2.11 通知公告表 announcements
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS announcements (
    announcement_id VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '公告ID(UUID hex)',
    title           VARCHAR(200)  NOT NULL COMMENT '公告标题',
    content         LONGTEXT      NOT NULL COMMENT '公告内容',
    priority        ENUM('normal','important','urgent')
                                  NOT NULL DEFAULT 'normal' COMMENT '优先级',
    target_type     ENUM('all','department','role')
                                  NOT NULL DEFAULT 'all' COMMENT '目标类型',
    target_ids      JSON          DEFAULT NULL COMMENT '目标ID列表(部门/角色)',
    attachment      VARCHAR(500)  DEFAULT NULL COMMENT '附件路径',
    published_by    VARCHAR(64)   NOT NULL COMMENT '发布者用户ID',
    published_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',

    INDEX idx_published_by (published_by),
    INDEX idx_published_at (published_at),
    INDEX idx_priority (priority),

    CONSTRAINT fk_announcement_publisher
        FOREIGN KEY (published_by) REFERENCES users(user_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='通知公告表';

-- -----------------------------------------------------------
-- 2.12 公告已读表 announcement_reads
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS announcement_reads (
    read_id         VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '已读记录ID(UUID hex)',
    announcement_id VARCHAR(64)   NOT NULL COMMENT '公告ID',
    user_id         VARCHAR(64)   NOT NULL COMMENT '用户ID',
    is_read         TINYINT(1)    NOT NULL DEFAULT 0 COMMENT '是否已读',
    read_at         DATETIME      DEFAULT NULL COMMENT '阅读时间',
    remind_count    INT           NOT NULL DEFAULT 0 COMMENT '提醒次数',

    UNIQUE INDEX idx_announcement_user (announcement_id, user_id),
    INDEX idx_user_id (user_id),

    CONSTRAINT fk_read_announcement
        FOREIGN KEY (announcement_id) REFERENCES announcements(announcement_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_read_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='公告已读记录表';

-- -----------------------------------------------------------
-- 2.13 审计日志表 audit_logs
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id          VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '日志ID(UUID hex)',
    user_id         VARCHAR(64)   NOT NULL COMMENT '操作用户ID',
    action          VARCHAR(100)  NOT NULL COMMENT '操作类型',
    resource_type   VARCHAR(50)   NOT NULL COMMENT '资源类型',
    resource_id     VARCHAR(64)   DEFAULT NULL COMMENT '资源ID',
    detail          JSON          DEFAULT NULL COMMENT '操作详情(JSON)',
    ip_address      VARCHAR(45)   DEFAULT NULL COMMENT 'IP地址',
    user_agent      VARCHAR(500)  DEFAULT NULL COMMENT 'User-Agent',
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',

    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_resource (resource_type, resource_id),
    INDEX idx_created_at (created_at),

    CONSTRAINT fk_audit_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='审计日志表';

-- -----------------------------------------------------------
-- 2.14 员工数据敏感度配置表 employee_data_sensitivity
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS employee_data_sensitivity (
    field_id        INT           NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT '字段配置ID',
    field_name      VARCHAR(100)  NOT NULL COMMENT '字段名(英文)',
    field_label     VARCHAR(100)  NOT NULL COMMENT '字段标签(中文)',
    sensitivity_level ENUM('public','department','private')
                                  NOT NULL DEFAULT 'public' COMMENT '敏感度级别',
    source_table    VARCHAR(100)  NOT NULL COMMENT '来源表名',
    source_column   VARCHAR(100)  NOT NULL COMMENT '来源列名',
    is_active       TINYINT(1)    NOT NULL DEFAULT 1 COMMENT '是否启用',
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_source_table (source_table),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='员工数据敏感度配置表(二期预留)';


-- ════════════════════════════════════════════════════════════
-- 三、默认数据
-- ════════════════════════════════════════════════════════════

-- 3.1 根部门
INSERT INTO departments (department_id, name, parent_id, sort_order) VALUES
    ('root', '总公司', NULL, 0)
ON DUPLICATE KEY UPDATE name = VALUES(name);

-- 3.2 默认管理员用户
-- 密码: Admin@123456
-- bcrypt hash (rounds=12) 通过 Python 生成:
--   from app.core.security import hash_password
--   print(hash_password("Admin@123456"))
-- 此处为预计算的 bcrypt hash，生产环境请务必更换密码!
INSERT INTO users (
    user_id, employee_id, name, email, phone,
    password_hash, role, department_id, job_level,
    hire_date, work_location, marital_status, status
) VALUES (
    'admin001', 'ADMIN001', '系统管理员', 'admin@company.com', '13800000000',
    '$2b$12$kp9uRPmMV1FgfsmBh.qPauJA4cp1qc3Sh1VnxHEfBVdkNQfpzLCeG',
    'admin', 'root', 'M3',
    '2024-01-01', '总部', 'single', 'active'
) ON DUPLICATE KEY UPDATE name = VALUES(name);

-- 测试账号 (账号: 123, 密码: 123, 角色: admin)
INSERT INTO users (
    user_id, employee_id, name, email, phone,
    password_hash, role, department_id, job_level,
    hire_date, work_location, marital_status, status
) VALUES (
    'user123', '123', '测试用户', NULL, NULL,
    '$2b$12$hSlAhczG0vrt4WMUAmeiI.2P3MppnF0CBOvFIrbR.KjIcNVpYAk22',
    'admin', 'root', NULL,
    '2024-01-01', '总部', NULL, 'active'
) ON DUPLICATE KEY UPDATE name = VALUES(name);

-- HR专员账号 (账号: HR001, 密码: Hr@123456, 角色: hr_specialist)
INSERT INTO users (
    user_id, employee_id, name, email, phone,
    password_hash, role, department_id, job_level,
    hire_date, work_location, marital_status, status
) VALUES (
    'hr001', 'HR001', '张HR', 'hr@company.com', '13800000001',
    '$2b$12$IlEBGdtiluBEo.SQEaw.Oem4hwRrogY0Yg9CgAzMfvuaZcuH5Ic/S',
    'hr_specialist', 'root', 'M2',
    '2024-03-01', '总部', 'married', 'active'
) ON DUPLICATE KEY UPDATE name = VALUES(name);

-- 3.3 预置分类
INSERT INTO categories (category_id, name, parent_id, type, access_level, sort_order) VALUES
    -- 文档分类（制度文档）
    ('cat_doc_root', '制度文档', NULL, 'document', 'all_roles', 0),
    ('cat_doc_salary', '薪酬制度', 'cat_doc_root', 'document', 'hr_admin_only', 1),
    ('cat_doc_leave', '休假制度', 'cat_doc_root', 'document', 'all_roles', 2),
    ('cat_doc_perf', '绩效制度', 'cat_doc_root', 'document', 'all_roles', 3),
    ('cat_doc_benefit', '福利制度', 'cat_doc_root', 'document', 'all_roles', 4),
    ('cat_doc_recruit', '招聘制度', 'cat_doc_root', 'document', 'all_roles', 5),
    ('cat_doc_train', '培训制度', 'cat_doc_root', 'document', 'all_roles', 6),
    ('cat_doc_attend', '考勤制度', 'cat_doc_root', 'document', 'all_roles', 7),
    ('cat_doc_contract', '劳动合同', 'cat_doc_root', 'document', 'hr_admin_only', 8),
    ('cat_doc_insurance', '社保公积金', 'cat_doc_root', 'document', 'all_roles', 9),
    ('cat_doc_handbook', '员工手册', 'cat_doc_root', 'document', 'all_roles', 10),
    ('cat_doc_reward', '奖惩制度', 'cat_doc_root', 'document', 'all_roles', 11),
    ('cat_doc_promote', '晋升制度', 'cat_doc_root', 'document', 'all_roles', 12),
    ('cat_doc_offboard', '离职制度', 'cat_doc_root', 'document', 'hr_admin_only', 13),
    ('cat_doc_safe', '安全生产', 'cat_doc_root', 'document', 'all_roles', 14),
    -- FAQ分类
    ('cat_faq_root', '常见问题', NULL, 'faq', 'all_roles', 50),
    ('cat_faq_salary', '薪酬FAQ', 'cat_faq_root', 'faq', 'hr_admin_only', 51),
    ('cat_faq_leave', '休假FAQ', 'cat_faq_root', 'faq', 'all_roles', 52),
    ('cat_faq_perf', '绩效FAQ', 'cat_faq_root', 'faq', 'all_roles', 53),
    ('cat_faq_benefit', '福利FAQ', 'cat_faq_root', 'faq', 'all_roles', 54),
    ('cat_faq_recruit', '招聘FAQ', 'cat_faq_root', 'faq', 'all_roles', 55),
    ('cat_faq_train', '培训FAQ', 'cat_faq_root', 'faq', 'all_roles', 56)
ON DUPLICATE KEY UPDATE name = VALUES(name);

-- 3.4 预置FAQ（常见问题及答案）
INSERT INTO faqs (faq_id, question, answer, category_id, related_doc_id, keywords, view_count, status, created_by) VALUES
    -- 考勤FAQ
    ('faq-attend-01', '每天的上下班时间是什么？',
     '公司实行标准工时制，每日工作时间为上午09:00—12:00，下午13:00—18:00（含午休1小时），每日标准工作时长为8小时。部分岗位经部门负责人批准可实行弹性工作制，核心工作时间为10:00—16:00。',
     'cat_faq_root', NULL, '上下班 时间 考勤', 0, 'active', 'user-admin-001'),
    ('faq-attend-02', '迟到会有什么处罚？',
     '月累计迟到1-2次给予口头提醒；3-5次每次扣款30元并书面警告；6次及以上视为严重违纪，扣发当月全勤奖并纳入绩效考核负面记录。迟到超过30分钟以上且未说明合理理由的按旷工半天处理。',
     'cat_faq_root', NULL, '迟到 处罚 扣款', 0, 'active', 'user-admin-001'),
    ('faq-attend-03', '如何申请加班？',
     '加班须提前填写《加班申请单》，经部门负责人审批后报人力资源部备案，未经审批的不视为加班。平时延长工作时间按150%支付加班工资，休息日加班按200%支付（或安排调休），法定节假日按300%支付。',
     'cat_faq_root', NULL, '加班 申请 加班费', 0, 'active', 'user-admin-001'),

    -- 薪酬FAQ
    ('faq-salary-01', '工资什么时候发放？',
     '公司实行月薪制，每月15日发放上月工资（遇节假日顺延）。工资包括基本工资、岗位津贴、绩效工资等组成部分。',
     'cat_faq_salary', NULL, '工资 发放 时间 发薪日', 0, 'active', 'user-admin-001'),
    ('faq-salary-02', '什么是全勤奖？如何获得？',
     '当月无迟到、早退、旷工、请假（年假除外）记录的员工可享受全勤奖200元/月。法定假期（年假、婚假、产假、丧假等）不影响全勤奖。',
     'cat_faq_salary', NULL, '全勤奖 条件 金额', 0, 'active', 'user-admin-001'),

    -- 休假FAQ
    ('faq-leave-01', '年假有多少天？怎么计算？',
     '员工累计工作满1年不满10年的，年休假5天；满10年不满20年的，年休假10天；满20年的，年休假15天。年假须提前5个工作日申请，经部门负责人审批后执行。',
     'cat_faq_leave', NULL, '年假 休假 天数 计算', 0, 'active', 'user-admin-001'),
    ('faq-leave-02', '婚假、产假怎么规定的？',
     '员工依法办理结婚登记的享受婚假3天；女职工生育享受不少于98天产假，难产或多胞胎生育的按国家规定增加；男职工享陪产假15天。',
     'cat_faq_leave', NULL, '婚假 产假 陪产假', 0, 'active', 'user-admin-001'),
    ('faq-leave-03', '病假和事假有什么区别？',
     '病假需凭医院证明申请，公司给予每年5天全薪病假，超出部分按薪酬制度执行。事假为无薪假期，须提前申请并获批准，原则上每月不超过2天。',
     'cat_faq_leave', NULL, '病假 事假 区别', 0, 'active', 'user-admin-001'),

    -- 福利FAQ
    ('faq-benefit-01', '公司有哪些福利？',
     '公司福利包括：五险一金、补充医疗保险（年度报销上限2万元）、意外伤害保险（保额20万）、年度健康体检、节日福利（300-500元/人）、生日礼金200元、结婚礼金1000元、住房补贴（500-1500元/月）、员工心理援助计划（EAP）等。',
     'cat_faq_benefit', NULL, '福利 五险一金 保险 体检 补贴', 0, 'active', 'user-admin-001'),
    ('faq-benefit-02', '年度体检什么时候安排？',
     '公司每年组织一次员工健康体检，具体时间由人力资源部统一安排并提前通知。体检费用由公司承担：普通员工800元/人，40岁以上员工1200元/人。',
     'cat_faq_benefit', NULL, '体检 安排 时间', 0, 'active', 'user-admin-001'),

    -- 绩效FAQ
    ('faq-perf-01', '绩效考核怎么评定？',
     '绩效考核采用季度考核与年度考核相结合的方式。考核指标包括工作业绩（60%）、工作能力（20%）、工作态度（20%）三个维度。考核结果分为S/A/B/C/D五个等级，直接关联晋升和奖金。',
     'cat_faq_perf', NULL, '绩效 考核 评定 等级', 0, 'active', 'user-admin-001'),
    ('faq-perf-02', '晋升需要什么条件？',
     '晋升需满足：1）在当前岗位任职满1年以上；2）近两次绩效考核评级均在A级以上；3）通过晋升评审委员会评审。职级每晋升一级，基本工资相应上调10%-20%。',
     'cat_faq_perf', NULL, '晋升 条件 职级', 0, 'active', 'user-admin-001')
ON DUPLICATE KEY UPDATE question = VALUES(question);

-- 3.4 敏感度配置（预置常用字段）
INSERT INTO employee_data_sensitivity (field_name, field_label, sensitivity_level, source_table, source_column) VALUES
    ('name', '姓名', 'public', 'users', 'name'),
    ('employee_id', '工号', 'public', 'users', 'employee_id'),
    ('email', '邮箱', 'department', 'users', 'email'),
    ('phone', '手机号', 'private', 'users', 'phone'),
    ('job_level', '职级', 'department', 'users', 'job_level'),
    ('hire_date', '入职日期', 'department', 'users', 'hire_date'),
    ('work_location', '工作地', 'department', 'users', 'work_location'),
    ('marital_status', '婚姻状态', 'private', 'users', 'marital_status')
ON DUPLICATE KEY UPDATE field_label = VALUES(field_label);
