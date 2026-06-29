-- ============================================================
-- HR制度智能问答系统 - 数据库初始化 DDL (MySQL 8.0)
-- ============================================================

CREATE DATABASE IF NOT EXISTS hr_policy_qa DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hr_policy_qa;

-- 1. 部门表
CREATE TABLE IF NOT EXISTS departments (
    department_id   VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '部门唯一标识(UUID)',
    name            VARCHAR(100)  NOT NULL COMMENT '部门名称',
    parent_id       VARCHAR(64)   NULL COMMENT '上级部门ID(树形结构)',
    sort_order      INT           DEFAULT 0 COMMENT '排序号',
    INDEX idx_dept_parent (parent_id),
    CONSTRAINT fk_dept_parent FOREIGN KEY (parent_id) REFERENCES departments(department_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='部门表';

-- 2. 用户表
CREATE TABLE IF NOT EXISTS users (
    user_id         VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '用户唯一标识(UUID)',
    employee_id     VARCHAR(20)   NOT NULL COMMENT '工号',
    name            VARCHAR(50)   NOT NULL COMMENT '姓名',
    email           VARCHAR(100)  NULL COMMENT '邮箱',
    phone           VARCHAR(15)   NULL COMMENT '手机号',
    password_hash   VARCHAR(255)  NOT NULL COMMENT '密码哈希(bcrypt)',
    role            ENUM('employee','hr_specialist','admin') NOT NULL DEFAULT 'employee' COMMENT '角色',
    department_id   VARCHAR(64)   NOT NULL COMMENT '所属部门ID',
    job_level       VARCHAR(20)   NULL COMMENT '职级(如P5/P6/M1/M2)',
    hire_date       DATE          NOT NULL COMMENT '入职日期',
    work_location   VARCHAR(50)   NULL COMMENT '工作地',
    marital_status  ENUM('single','married') NULL COMMENT '婚姻状态',
    status          ENUM('active','disabled') NOT NULL DEFAULT 'active' COMMENT '账号状态',
    login_attempts  INT           DEFAULT 0 COMMENT '连续登录失败次数',
    locked_until    DATETIME      NULL COMMENT '锁定截止时间',
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_employee_id (employee_id),
    INDEX idx_users_email (email),
    INDEX idx_users_department (department_id),
    INDEX idx_users_role (role),
    CONSTRAINT fk_users_dept FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 3. 分类标签表
CREATE TABLE IF NOT EXISTS categories (
    category_id     VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '分类ID(UUID)',
    name            VARCHAR(100)  NOT NULL COMMENT '分类名称',
    parent_id       VARCHAR(64)   NULL COMMENT '上级分类ID',
    type            ENUM('document','faq') NOT NULL COMMENT '分类类型',
    access_level    ENUM('all_roles','hr_admin_only','admin_only') NOT NULL DEFAULT 'all_roles' COMMENT '默认检索权限级别',
    sort_order      INT           DEFAULT 0 COMMENT '排序号',
    INDEX idx_cat_parent (parent_id),
    INDEX idx_cat_type (type),
    CONSTRAINT fk_cat_parent FOREIGN KEY (parent_id) REFERENCES categories(category_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='分类标签表';

-- 4. 制度文档表
CREATE TABLE IF NOT EXISTS documents (
    document_id     VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '文档唯一标识(UUID)',
    title           VARCHAR(200)  NOT NULL COMMENT '文档标题',
    content         LONGTEXT      NOT NULL COMMENT '解析后的文本内容',
    category_id     VARCHAR(64)   NOT NULL COMMENT '分类ID',
    format          ENUM('pdf','word','markdown','html') NOT NULL COMMENT '原始格式',
    version         VARCHAR(10)   NOT NULL DEFAULT '1.0' COMMENT '版本号',
    version_note    VARCHAR(500)  NULL COMMENT '版本变更说明',
    status          ENUM('draft','published','archived') NOT NULL DEFAULT 'draft' COMMENT '文档状态',
    access_level    ENUM('inherit','all_roles','hr_admin_only','admin_only') NOT NULL DEFAULT 'inherit' COMMENT '检索权限级别',
    uploaded_by     VARCHAR(64)   NOT NULL COMMENT '上传者用户ID',
    file_path       VARCHAR(500)  NOT NULL COMMENT '原始文件存储路径',
    word_count      INT           DEFAULT 0 COMMENT '字数统计',
    chunk_count     INT           DEFAULT 0 COMMENT '分块数量(二期)',
    embedding_status VARCHAR(20)  DEFAULT 'pending' COMMENT '向量化状态:pending/processing/completed/failed',
    published_at    DATETIME      NULL COMMENT '发布时间',
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_docs_category (category_id),
    INDEX idx_docs_status (status),
    INDEX idx_docs_access (access_level),
    INDEX idx_docs_uploaded (uploaded_by),
    FULLTEXT INDEX ft_docs_content (title, content) WITH PARSER ngram,
    CONSTRAINT fk_docs_category FOREIGN KEY (category_id) REFERENCES categories(category_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_docs_uploader FOREIGN KEY (uploaded_by) REFERENCES users(user_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='制度文档表';

-- 5. 文档版本历史表
CREATE TABLE IF NOT EXISTS document_versions (
    version_id      VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '版本记录ID(UUID)',
    document_id     VARCHAR(64)   NOT NULL COMMENT '关联文档ID',
    version         VARCHAR(10)   NOT NULL COMMENT '版本号',
    content_snapshot LONGTEXT     NOT NULL COMMENT '该版本内容快照',
    change_summary  VARCHAR(1000) NULL COMMENT '变更摘要',
    changed_by      VARCHAR(64)   NOT NULL COMMENT '变更人ID',
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '版本创建时间',
    INDEX idx_ver_doc (document_id),
    CONSTRAINT fk_ver_document FOREIGN KEY (document_id) REFERENCES documents(document_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ver_changer FOREIGN KEY (changed_by) REFERENCES users(user_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文档版本历史表';

-- 6. 文档块表 (RAG分块, 一期预建)
CREATE TABLE IF NOT EXISTS document_chunks (
    chunk_id        VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '块ID(UUID)',
    document_id     VARCHAR(64)   NOT NULL COMMENT '关联文档ID',
    chunk_index     INT           NOT NULL COMMENT '块序号(从0开始)',
    content         TEXT          NOT NULL COMMENT '块文本内容',
    token_count     INT           DEFAULT 0 COMMENT 'Token数量估算',
    embedding_status VARCHAR(20)  DEFAULT 'pending' COMMENT '向量化状态:pending/processing/completed/failed',
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_chunks_doc (document_id),
    INDEX idx_chunks_status (embedding_status),
    CONSTRAINT fk_chunks_document FOREIGN KEY (document_id) REFERENCES documents(document_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文档块表(RAG分块)';

-- 7. FAQ表
CREATE TABLE IF NOT EXISTS faqs (
    faq_id          VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT 'FAQ ID(UUID)',
    question        VARCHAR(500)  NOT NULL COMMENT '问题标题',
    answer          TEXT          NOT NULL COMMENT '标准答案(富文本)',
    category_id     VARCHAR(64)   NOT NULL COMMENT 'FAQ分类ID',
    related_doc_id  VARCHAR(64)   NULL COMMENT '关联制度文档ID',
    keywords        VARCHAR(500)  NULL COMMENT '关键词(逗号分隔)',
    view_count      INT           DEFAULT 0 COMMENT '被匹配/查看次数',
    status          ENUM('active','archived') NOT NULL DEFAULT 'active' COMMENT '状态',
    created_by      VARCHAR(64)   NOT NULL COMMENT '创建者',
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_faq_category (category_id),
    INDEX idx_faq_status (status),
    FULLTEXT INDEX ft_faq_search (question, keywords) WITH PARSER ngram,
    CONSTRAINT fk_faq_category FOREIGN KEY (category_id) REFERENCES categories(category_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_faq_document FOREIGN KEY (related_doc_id) REFERENCES documents(document_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_faq_creator FOREIGN KEY (created_by) REFERENCES users(user_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='FAQ表';

-- 8. 会话表
CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id      VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '会话ID(UUID)',
    user_id         VARCHAR(64)   NOT NULL COMMENT '用户ID',
    title           VARCHAR(200)  NULL COMMENT '会话标题(默认取首条问题)',
    is_pinned       TINYINT(1)    DEFAULT 0 COMMENT '是否置顶',
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_chat_user (user_id),
    INDEX idx_chat_pinned (is_pinned),
    CONSTRAINT fk_chat_user FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='会话表';

-- 9. 问答记录表
CREATE TABLE IF NOT EXISTS qa_records (
    record_id       VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '记录ID(UUID)',
    user_id         VARCHAR(64)   NOT NULL COMMENT '提问用户ID',
    session_id      VARCHAR(64)   NOT NULL COMMENT '会话ID(多轮对话关联)',
    question        TEXT          NOT NULL COMMENT '用户问题原文',
    answer          TEXT          NOT NULL COMMENT '系统完整回答',
    answer_type     ENUM('faq','rule','search','rag','no_result') NOT NULL COMMENT '回答类型',
    confidence      DECIMAL(3,2)  NULL COMMENT 'RAG回答置信度(0.00-1.00)',
    reference_docs  JSON          NULL COMMENT '参考文档列表',
    response_time_ms INT          DEFAULT 0 COMMENT '响应时间(毫秒)',
    feedback        ENUM('helpful','not_helpful') NULL COMMENT '用户反馈',
    feedback_reason VARCHAR(500)  NULL COMMENT '负面反馈原因',
    is_favorite     TINYINT(1)    DEFAULT 0 COMMENT '是否收藏',
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_qa_user (user_id),
    INDEX idx_qa_session (session_id),
    INDEX idx_qa_created (created_at),
    INDEX idx_qa_type (answer_type),
    CONSTRAINT fk_qa_user FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='问答记录表';

-- 9. 纠错申请表
CREATE TABLE IF NOT EXISTS correction_requests (
    request_id      VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '申请ID(UUID)',
    document_id     VARCHAR(64)   NOT NULL COMMENT '关联文档ID',
    section         VARCHAR(500)  NOT NULL COMMENT '问题段落定位',
    description     TEXT          NOT NULL COMMENT '纠错说明',
    submitted_by    VARCHAR(64)   NOT NULL COMMENT '提交人ID',
    reviewed_by     VARCHAR(64)   NULL COMMENT '审核人ID',
    status          ENUM('pending','approved','rejected') NOT NULL DEFAULT 'pending' COMMENT '审核状态',
    review_comment  VARCHAR(500)  NULL COMMENT '审核意见',
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
    reviewed_at     DATETIME      NULL COMMENT '审核时间',
    INDEX idx_corr_doc (document_id),
    INDEX idx_corr_status (status),
    INDEX idx_corr_submitter (submitted_by),
    CONSTRAINT fk_corr_document FOREIGN KEY (document_id) REFERENCES documents(document_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_corr_submitter FOREIGN KEY (submitted_by) REFERENCES users(user_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_corr_reviewer FOREIGN KEY (reviewed_by) REFERENCES users(user_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='纠错申请表';

-- 10. 通知公告表
CREATE TABLE IF NOT EXISTS announcements (
    announcement_id VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '公告ID(UUID)',
    title           VARCHAR(200)  NOT NULL COMMENT '公告标题',
    content         TEXT          NOT NULL COMMENT '公告内容(富文本)',
    priority        ENUM('normal','important','urgent') NOT NULL DEFAULT 'normal' COMMENT '优先级',
    target_type     ENUM('all','department','role') NOT NULL DEFAULT 'all' COMMENT '推送范围类型',
    target_ids      JSON          NULL COMMENT '目标范围ID列表',
    attachment      VARCHAR(500)  NULL COMMENT '附件路径',
    published_by    VARCHAR(64)   NOT NULL COMMENT '发布人ID',
    published_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
    INDEX idx_ann_publisher (published_by),
    INDEX idx_ann_published (published_at),
    CONSTRAINT fk_ann_publisher FOREIGN KEY (published_by) REFERENCES users(user_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='通知公告表';

-- 11. 公告阅读记录表
CREATE TABLE IF NOT EXISTS announcement_reads (
    read_id         VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '记录ID(UUID)',
    announcement_id VARCHAR(64)   NOT NULL COMMENT '公告ID',
    user_id         VARCHAR(64)   NOT NULL COMMENT '用户ID',
    is_read         TINYINT(1)    DEFAULT 0 COMMENT '是否已读',
    read_at         DATETIME      NULL COMMENT '阅读时间',
    remind_count    INT           DEFAULT 0 COMMENT '提醒次数',
    UNIQUE KEY uk_ann_user (announcement_id, user_id),
    INDEX idx_ar_user (user_id),
    CONSTRAINT fk_ar_announcement FOREIGN KEY (announcement_id) REFERENCES announcements(announcement_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ar_user FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='公告阅读记录表';

-- 12. 审计日志表
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id          VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '日志ID(UUID)',
    user_id         VARCHAR(64)   NOT NULL COMMENT '操作用户ID',
    action          VARCHAR(100)  NOT NULL COMMENT '操作类型(如:login/document_create/faq_update等)',
    resource_type   VARCHAR(50)   NOT NULL COMMENT '资源类型(如:user/document/faq等)',
    resource_id     VARCHAR(64)   NULL COMMENT '资源ID',
    detail          JSON          NULL COMMENT '操作详情(变更前后快照)',
    ip_address      VARCHAR(45)   NULL COMMENT '操作IP',
    user_agent      VARCHAR(500)  NULL COMMENT '浏览器UserAgent',
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    INDEX idx_audit_user (user_id),
    INDEX idx_audit_action (action),
    INDEX idx_audit_created (created_at),
    INDEX idx_audit_resource (resource_type, resource_id),
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审计日志表';

-- 13. 员工数据敏感度配置表（二期）
CREATE TABLE IF NOT EXISTS employee_data_sensitivity (
    field_id        INT           NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
    field_name      VARCHAR(100)  NOT NULL COMMENT '字段英文名',
    field_label     VARCHAR(100)  NOT NULL COMMENT '字段中文名',
    sensitivity_level ENUM('public','department','private') NOT NULL DEFAULT 'public' COMMENT '敏感度级别',
    source_table    VARCHAR(100)  NOT NULL COMMENT '数据源表',
    source_column   VARCHAR(100)  NOT NULL COMMENT '数据源列',
    is_active       TINYINT(1)    DEFAULT 1 COMMENT '是否启用',
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='员工数据字段敏感度配置表';

-- ============================================================
-- 初始化预置数据
-- ============================================================

-- 预置部门
INSERT INTO departments (department_id, name, parent_id, sort_order) VALUES
('dept-001', '总公司', NULL, 0),
('dept-002', '技术部', 'dept-001', 1),
('dept-003', '产品部', 'dept-001', 2),
('dept-004', '人力资源部', 'dept-001', 3),
('dept-005', '财务部', 'dept-001', 4);

-- 预置文档分类 (树形)
INSERT INTO categories (category_id, name, parent_id, type, access_level, sort_order) VALUES
('cat-root-doc', '制度分类', NULL, 'document', 'all_roles', 0),
('cat-doc-1', '考勤制度', 'cat-root-doc', 'document', 'all_roles', 1),
('cat-doc-1-1', '打卡管理', 'cat-doc-1', 'document', 'all_roles', 1),
('cat-doc-1-2', '加班政策', 'cat-doc-1', 'document', 'all_roles', 2),
('cat-doc-1-3', '调休规定', 'cat-doc-1', 'document', 'all_roles', 3),
('cat-doc-2', '薪酬制度', 'cat-root-doc', 'document', 'hr_admin_only', 2),
('cat-doc-2-1', '薪资结构', 'cat-doc-2', 'document', 'hr_admin_only', 1),
('cat-doc-2-2', '奖金发放', 'cat-doc-2', 'document', 'hr_admin_only', 2),
('cat-doc-2-3', '个税说明', 'cat-doc-2', 'document', 'hr_admin_only', 3),
('cat-doc-3', '福利制度', 'cat-root-doc', 'document', 'all_roles', 3),
('cat-doc-3-1', '健康体检', 'cat-doc-3', 'document', 'all_roles', 1),
('cat-doc-3-2', '补贴标准', 'cat-doc-3', 'document', 'all_roles', 2),
('cat-doc-3-3', '弹性福利', 'cat-doc-3', 'document', 'all_roles', 3),
('cat-doc-4', '休假制度', 'cat-root-doc', 'document', 'all_roles', 4),
('cat-doc-4-1', '年假规定', 'cat-doc-4', 'document', 'all_roles', 1),
('cat-doc-4-2', '病假规定', 'cat-doc-4', 'document', 'all_roles', 2),
('cat-doc-4-3', '婚假/产假', 'cat-doc-4', 'document', 'all_roles', 3),
('cat-doc-4-4', '其他假期', 'cat-doc-4', 'document', 'all_roles', 4),
('cat-doc-5', '绩效制度', 'cat-root-doc', 'document', 'hr_admin_only', 5),
('cat-doc-5-1', '考核周期', 'cat-doc-5', 'document', 'hr_admin_only', 1),
('cat-doc-5-2', '晋升条件', 'cat-doc-5', 'document', 'hr_admin_only', 2);

-- 预置FAQ分类
INSERT INTO categories (category_id, name, parent_id, type, access_level, sort_order) VALUES
('cat-root-faq', 'FAQ分类', NULL, 'faq', 'all_roles', 0),
('cat-faq-1', '考勤FAQ', 'cat-root-faq', 'faq', 'all_roles', 1),
('cat-faq-2', '薪酬FAQ', 'cat-root-faq', 'faq', 'all_roles', 2),
('cat-faq-3', '休假FAQ', 'cat-root-faq', 'faq', 'all_roles', 3),
('cat-faq-4', '福利FAQ', 'cat-root-faq', 'faq', 'all_roles', 4),
('cat-faq-5', '绩效FAQ', 'cat-root-faq', 'faq', 'all_roles', 5);

-- 预置管理员账号 (密码: Admin@123, bcrypt hash)
INSERT INTO users (user_id, employee_id, name, email, password_hash, role, department_id, hire_date, status) VALUES
('user-admin-001', 'admin001', '系统管理员', 'admin@company.com',
 '$2b$12$lsXQnZBZ.65gdiE1R0wOsO8bfjoGa8/M2kY.VHCqWy4cmk8jQLm0u',
 'admin', 'dept-004', '2020-01-01', 'active');

-- 员工数据敏感度配置（16个预设字段，三级敏感度）
INSERT INTO employee_data_sensitivity (field_name, field_label, sensitivity_level, source_table, source_column, is_active) VALUES
('employee_id', '工号', 'public', 'users', 'employee_id', 1),
('name', '姓名', 'public', 'users', 'name', 1),
('department_name', '部门', 'public', 'users', 'department_id', 1),
('job_title', '岗位名称', 'public', 'users', '', 1),
('job_level', '职级', 'department', 'users', 'job_level', 1),
('hire_date', '入职日期', 'department', 'users', 'hire_date', 1),
('work_location', '工作地', 'public', 'users', 'work_location', 1),
('email', '邮箱', 'department', 'users', 'email', 1),
('phone', '手机号', 'private', 'users', 'phone', 1),
('marital_status', '婚姻状况', 'private', 'users', 'marital_status', 1),
('manager_name', '直属上级', 'department', 'users', '', 1),
('work_years', '工龄', 'department', 'users', '', 1),
('salary', '工资', 'private', 'users', '', 0),
('bonus', '奖金', 'private', 'users', '', 0),
('performance_grade', '绩效等级', 'private', 'users', '', 0),
('id_card', '身份证号', 'private', 'users', '', 0);
