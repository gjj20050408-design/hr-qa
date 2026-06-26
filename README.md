# HR 制度智能问答系统

基于 RAG（检索增强生成）的 HR 政策智能问答平台，支持文档管理、全文搜索、FAQ 匹配、智能问答、多轮对话、数据驾驶舱等功能。

## 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Vue 3.4 + TypeScript + Element Plus + ECharts + Vite 5 |
| **后端** | FastAPI + SQLAlchemy 2.0 + Celery + Redis |
| **数据库** | MySQL 8.0 |
| **向量数据库** | ChromaDB |
| **AI/分词** | OpenAI API + Jieba |
| **部署** | Docker Compose (Nginx + Backend + MySQL + Redis + Celery) |

## 项目结构

```
.
├── backend/                # 后端 (FastAPI)
│   ├── app/
│   │   ├── api/v1/         # API 路由层
│   │   ├── core/           # 核心模块 (配置, 数据库, Redis, 安全)
│   │   ├── models/         # SQLAlchemy 数据模型
│   │   ├── schemas/        # Pydantic 请求/响应模型
│   │   ├── services/       # 业务逻辑层
│   │   ├── providers/      # AI 提供者抽象层
│   │   ├── middleware/     # 中间件
│   │   ├── tasks/          # Celery 异步任务
│   │   └── utils/          # 工具函数
│   ├── init_db.sql         # 数据库初始化脚本
│   ├── requirements.txt    # Python 依赖
│   └── .env                # 环境变量配置
├── frontend/               # 前端 (Vue 3)
│   ├── src/
│   │   ├── views/          # 页面组件 (18 个)
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # Pinia 状态管理
│   │   └── api/            # API 请求封装
│   └── package.json
├── mysql/                  # MySQL 配置
├── nginx/                  # Nginx 配置
├── scripts/                # 初始化 & 启动脚本
├── docs/                   # 项目文档
├── prd/                    # PRD 文档
├── architecture/           # 架构设计文档
└── docker-compose.yml      # Docker 编排
```

## 环境要求

| 工具 | 最低版本 | 说明 |
|------|----------|------|
| **Conda** (Miniconda/Anaconda) | 最新版 | Python 环境管理 |
| **Node.js** | 18.x+ | 前端构建 |
| **npm** | 9.x+ | 前端包管理 |
| **MySQL** | 8.0+ | 数据库（本地安装 / Docker 均可） |
| **Redis** | 7+ | 缓存队列（本地安装 / Docker 均可） |
| **Git** | 2.x+ | 版本控制 |

## 快速开始

### 1. 克隆项目

```bash
git clone https://gitee.com/pure-dhmo/hr.git
cd hr
```

### 2. 一键初始化

**Windows：**

```cmd
scripts\init.cmd
```

**Linux / macOS：**

```bash
bash scripts/init.sh
```

初始化脚本将自动完成：
- 创建 Conda 环境 `hr-qa`（Python 3.11）
- 安装 Python 依赖
- 启动 MySQL + Redis（通过 Docker Compose）
- 初始化数据库（建库 + 建表 + 预置数据）
- 安装前端依赖

### 3. 启动服务

**Windows：**

```cmd
scripts\start.cmd
```

**Linux / macOS：**

```bash
bash scripts/start.sh
```

启动后访问：
- **前端页面**：http://localhost:5173
- **API 文档**：http://localhost:8000/api/docs
- **健康检查**：http://localhost:8000/api/v1/health

### 4. 预置账号

| 角色 | 工号 | 密码 |
|------|------|------|
| 管理员 | `admin001` | `Admin@123` |

## 手动初始化和启动

### 创建 Conda 环境

```bash
conda create -n hr-qa python=3.11 -y
conda activate hr-qa
pip install -r backend/requirements.txt
```

### 启动基础设施（MySQL + Redis）

```bash
docker compose up -d mysql redis
```

### 初始化数据库

```bash
# 等待 MySQL 启动后执行
docker exec -i hr-qa-mysql mysql -uroot -ppassword < backend/init_db.sql
```

### 启动后端

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 启动前端

```bash
cd frontend
npm install     # 首次运行需安装依赖
npm run dev
```

### 启动 Celery（可选）

```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

## Docker Compose 一键部署

```bash
docker compose up -d --build
```

访问 http://localhost

## 配置说明

主要配置文件为 `backend/.env`，关键配置项：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `DB_HOST` | `localhost` | 数据库地址 |
| `DB_PORT` | `3306` | 数据库端口 |
| `DB_USER` | `root` | 数据库用户 |
| `DB_PASSWORD` | `password` | 数据库密码 |
| `DB_NAME` | `hr_policy_qa` | 数据库名 |
| `REDIS_HOST` | `localhost` | Redis 地址 |
| `JWT_SECRET_KEY` | `change-me...` | 生产环境请更换 |
| `DEBUG` | `true` | 调试模式（生产关闭） |

## 相关文档

- [PRD 文档](./prd/)
- [系统架构设计说明书](./architecture/)
- [Git 团队协作规范](./docs/Git团队协作规范.md)
- [需求调研报告](./需求调研.md)
