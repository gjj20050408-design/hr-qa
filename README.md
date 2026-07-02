<div align="center">

# HR 制度智能问答系统

**基于 RAG 架构的企业 HR 政策知识库问答平台**

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Vue](https://img.shields.io/badge/Vue-3.4-42b883?logo=vue.js)](https://vuejs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178c6?logo=typescript)](https://typescriptlang.org)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479a1?logo=mysql)](https://mysql.com)
[![Redis](https://img.shields.io/badge/Redis-7.x-dc382d?logo=redis)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ed?logo=docker)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

[功能演示](#功能演示) · [架构设计](#系统架构) · [技术亮点](#技术亮点) · [快速开始](#快速开始) · [API 文档](#api-文档)

</div>

---

## 项目简介

本项目是一套面向企业 HR 场景的**智能政策问答系统**，员工可以通过自然语言提问，系统自动检索相关 HR 制度文档并给出准确答案。

核心思路是将企业 HR 文档（Word/PDF）向量化存入 ChromaDB，在问答时通过**多阶段责任链**依次执行：FAQ 精确匹配 → 规则引擎 → 权限过滤 → MySQL 全文检索 → RAG 语义检索 + LLM 生成，同时支持**多轮对话**上下文追问。

```
员工提问 → FAQ匹配(0ms) → 规则匹配 → 权限过滤 → 全文搜索 → RAG向量检索 → LLM生成 → 返回答案
                ↓                                                        ↓
          命中时直接返回                                           ChromaDB + OpenAI API
```

---

## 功能演示

| 角色 | 功能模块 |
|------|----------|
| **员工端** | 自然语言问答、多轮对话、历史会话、制度文档浏览、全文搜索、FAQ 查阅 |
| **HR 专员** | 文档上传与管理、FAQ 维护、问答记录审查、纠错反馈处理 |
| **管理员** | 用户部门管理、数据驾驶舱（ECharts 可视化）、系统公告、审计日志 |

---

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端  Vue 3 + TypeScript               │
│   Element Plus UI · Pinia 状态 · ECharts 数据可视化       │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP / REST
┌────────────────────────▼────────────────────────────────┐
│                 FastAPI 后端（异步）                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │  Auth    │  │  Docs    │  │   QA / Search / FAQ  │  │
│  │  JWT     │  │  Upload  │  │   责任链策略引擎       │  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐ │
│  │              Provider 抽象层                        │ │
│  │  LLMProvider(熔断器) · EmbeddingProvider · Chunker │ │
│  └────────────────────────────────────────────────────┘ │
└───┬────────────────────┬────────────────────────────────┘
    │                    │
┌───▼───┐  ┌────────┐  ┌▼─────────┐  ┌──────────┐
│MySQL 8│  │ Redis  │  │ ChromaDB │  │ Celery   │
│业务数据│  │缓存/限流│  │向量存储  │  │异步任务  │
└───────┘  └────────┘  └──────────┘  └──────────┘
```

---

## 技术亮点

### 1. 责任链模式 — 多阶段问答策略

问答核心采用**责任链（Chain of Responsibility）**设计模式，每个处理器专注单一职责，按优先级顺序传递，任意一环命中即短路返回：

```python
# backend/app/services/qa_chain.py
FAQ匹配 → 规则匹配 → 个人数据守卫 → 权限过滤 → 全文检索 → RAG语义检索 → 兜底回复
```

- **FAQMatcher**：基于 Jieba 分词的中文相似度匹配，阈值 ≥ 0.70 时精确命中
- **RuleMatcher**：正则规则引擎，覆盖固定格式问题（假期天数、工资日等）
- **PersonalDataGuard**：敏感数据分级访问控制，拦截越权查询
- **PermissionFilter**：基于 RBAC 权限矩阵过滤文档访问范围
- **SearchHandler**：MySQL `MATCH AGAINST` 全文索引检索
- **RAGHandler**：ChromaDB 向量相似度检索 + LLM 上下文生成
- **FallbackHandler**：兜底应答，避免空响应

### 2. 熔断器模式 — LLM 高可用

LLM 调用使用**熔断器（Circuit Breaker）**包装，防止 API 故障时级联超时：

```python
# backend/app/providers/llm.py — CircuitBreakerLLMProvider
连续失败 5 次 → 熔断打开（30s 拒绝请求）→ 半开探测 → 自动恢复
```

### 3. Provider 抽象层 — 可替换 AI 后端

LLM、Embedding、文档解析均抽象为 Protocol 接口，支持热替换：

```python
class LLMProvider(Protocol):
    def generate(self, prompt, history, ...) -> LLMResponse: ...

# 实现：OpenAI API / 本地模型 / NoOp(测试桩)
```

### 4. 多轮对话上下文管理

- 会话存储于 MySQL `chat_sessions` + `qa_records` 表
- 最多保留最近 5 轮历史，拼接为 LLM messages 上下文
- Redis 缓存热点会话，减少数据库查询

### 5. RBAC 权限矩阵

角色（员工/HR 专员/管理员）× 文档访问级别（公开/HR及以上/仅管理员）构成配置化权限矩阵，问答时自动过滤无权限文档：

```python
PERMISSION_MATRIX = {
    (AccessLevel.HR_ADMIN_ONLY, Role.EMPLOYEE): False,   # 员工不可见 HR 专属文档
    (AccessLevel.HR_ADMIN_ONLY, Role.HR_SPECIALIST): True,
    ...
}
```

### 6. 异步全链路

- FastAPI + SQLAlchemy 2.0 **全异步**（`async/await`），无阻塞 I/O
- Redis 限流：问答 20 次/分钟、搜索 30 次/分钟，防刷
- Celery + Redis 处理文档解析、向量化等耗时异步任务

---

## 技术栈

| 层级 | 技术选型 | 选型原因 |
|------|----------|----------|
| **前端框架** | Vue 3.4 + TypeScript | Composition API + 类型安全 |
| **前端 UI** | Element Plus + ECharts | 企业级组件库 + 丰富图表 |
| **前端状态** | Pinia + Vue Router 4 | 轻量、支持 Composition API |
| **后端框架** | FastAPI 0.110 | 原生异步、自动 OpenAPI 文档 |
| **ORM** | SQLAlchemy 2.0 | 全异步支持、类型提示完善 |
| **关系数据库** | MySQL 8.0 | 全文索引（FULLTEXT）+ 事务 |
| **向量数据库** | ChromaDB | 轻量嵌入式向量存储，无需独立部署 |
| **缓存 / 队列** | Redis 7 | 会话缓存 + 限流计数器 + Celery Broker |
| **异步任务** | Celery | 文档向量化等耗时任务异步化 |
| **AI 接口** | OpenAI Compatible API | 支持任意兼容 OpenAI 格式的模型 |
| **中文分词** | Jieba | FAQ 匹配与全文检索预处理 |
| **安全** | bcrypt + JWT | 密码哈希强度 12 轮 + 双 Token 机制 |
| **部署** | Docker Compose + Nginx | 一键全栈部署 |

---

## 项目结构

```
.
├── backend/
│   └── app/
│       ├── api/v1/          # 路由层（auth / docs / qa / admin / insights）
│       ├── core/            # 基础设施（config / database / redis / security）
│       ├── models/          # SQLAlchemy ORM 模型（15 张表）
│       ├── schemas/         # Pydantic 请求/响应 Schema
│       ├── services/        # 业务逻辑（qa_chain / search / faq / audit...）
│       ├── providers/       # AI 抽象层（llm / embedding / chunker / docx_parser）
│       ├── tasks/           # Celery 异步任务
│       ├── middleware/      # 异常处理 / 请求日志中间件
│       └── enums/           # 枚举 + 常量（权限矩阵 / 阈值 / 规则模板）
├── frontend/
│   └── src/
│       ├── views/           # 23 个页面组件（员工端 / 管理端）
│       ├── stores/          # Pinia store（auth / user）
│       ├── api/             # Axios 请求封装
│       └── router/          # 路由配置（含权限守卫）
├── mysql/                   # MySQL 配置（my.cnf）
├── nginx/                   # Nginx 反向代理配置
├── scripts/                 # 一键初始化 / 启动脚本
├── docs/                    # 团队协作规范、数据库文档
├── architecture/            # 系统架构设计说明书、详细设计文档
├── prd/                     # 产品需求文档
├── docker-compose.yml       # 全栈 Docker 编排
└── README.md
```

---

## 快速开始

### 环境要求

| 工具 | 版本 |
|------|------|
| Conda (Miniconda/Anaconda) | 最新版 |
| Node.js | 18.x+ |
| Docker & Docker Compose | 最新版 |

### 一键启动（推荐）

```bash
# 1. 克隆
git clone https://github.com/gjj20050408-design/hr-qa.git
cd hr-qa

# 2. 初始化（创建 Conda 环境 + 数据库 + 前端依赖）
scripts\init.cmd          # Windows
# bash scripts/init.sh   # Linux / macOS

# 3. 启动所有服务
scripts\start.cmd         # Windows
# bash scripts/start.sh  # Linux / macOS
```

启动后访问：

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:5173 |
| API 文档（Swagger） | http://localhost:8000/api/docs |
| 健康检查 | http://localhost:8000/api/v1/health |

### 预置账号

| 角色 | 工号 | 密码 |
|------|------|------|
| 管理员 | `admin001` | `Admin@123` |

### Docker 全栈部署

```bash
docker compose up -d --build
# 访问 http://localhost
```

---

## API 文档

后端基于 FastAPI 自动生成 OpenAPI 文档，启动后访问 `/api/docs` 即可在线调试。

主要接口模块：

| 模块 | 路径前缀 | 说明 |
|------|----------|------|
| 认证 | `/api/v1/auth` | 登录、刷新 Token、修改密码 |
| 问答 | `/api/v1/qa` | 提问、多轮追问、反馈、收藏 |
| 搜索 | `/api/v1/search` | 全文检索（含权限过滤） |
| 文档 | `/api/v1/documents` | 上传、解析、向量化、管理 |
| FAQ | `/api/v1/faqs` | 常见问题管理 |
| 管理 | `/api/v1/admin` | 用户 / 部门 / 公告管理 |
| 数据 | `/api/v1/insights` | 数据驾驶舱统计接口 |

---

## 数据库设计

系统共 15 张核心业务表，关键表结构：

```
users               员工账户（RBAC 角色、部门关联）
departments         部门树形结构
documents           HR 文档（含访问级别、解析状态）
document_chunks     文档分块（向量化粒度）
chat_sessions       会话（支持置顶、重命名）
qa_records          问答记录（含置信度、答案类型、引用文档）
faqs                常见问题库（分类、关键词）
audit_logs          操作审计日志
announcements       系统公告
```

---

## 环境变量配置

配置文件：`backend/.env`

```env
# 数据库
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=hr_policy_qa

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT（生产环境请替换）
JWT_SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=120
REFRESH_TOKEN_EXPIRE_DAYS=7

# OpenAI 兼容 API
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# 调试模式（生产关闭）
DEBUG=false
```

---

## 相关文档

- [系统架构设计说明书](./architecture/)
- [产品需求文档 PRD](./prd/)
- [详细数据库设计](./docs/)
- [Git 团队协作规范](./docs/Git团队协作规范.md)

---

<div align="center">

**如有问题欢迎提 Issue 或 PR**

</div>
