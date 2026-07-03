"""FastAPI 主应用入口"""
import logging
import os
import socket
import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine, Base, check_db_connection
from app.core.redis import init_redis, close_redis
from app.middleware.request_middleware import RequestIDMiddleware, ClientPlatformMiddleware
from app.middleware.exception_handler import global_exception_handler, validation_exception_handler

# 导入所有模型（确保 Base.metadata 包含全部表）
from app.models import *  # noqa: F401, F403

# 导入路由
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as documents_router
from app.api.v1.qa import router as qa_router
from app.api.v1.admin import router as admin_router
from app.api.v1.faqs import router as faqs_router
from app.api.v1.insights import router as insights_router

# 日志配置
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _is_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    """检测指定端口是否已被占用（即服务是否已启动）"""
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        return True
    except (OSError, ConnectionRefusedError):
        return False


def _start_redis() -> bool:
    """尝试自动启动 Redis 服务"""
    # 先检查端口是否已打开
    if _is_port_open(settings.REDIS_HOST, settings.REDIS_PORT):
        logger.info(f"Redis already running on {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        return True

    if not settings.REDIS_AUTO_START:
        return False

    redis_path = settings.REDIS_SERVER_PATH
    logger.info(f"Attempting to auto-start Redis: {redis_path}")
    try:
        subprocess.Popen(
            [redis_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        logger.info(f"Redis auto-start command sent (port {settings.REDIS_PORT})")
        return True
    except FileNotFoundError:
        logger.warning(
            f"Redis executable not found at '{redis_path}'. "
            "Please install Redis or set REDIS_SERVER_PATH to the correct path."
        )
    except Exception as e:
        logger.warning(f"Failed to auto-start Redis: {e}")
    return False


def _init_providers():
    """初始化 RAG 相关提供者（LLM/Embedding/VectorStore）"""
    try:
        # LLM 初始化（DeepSeek）
        llm_key = settings.LLM_API_KEY or ""
        llm_url = settings.LLM_BASE_URL or ""
        llm_model = settings.LLM_MODEL
        if llm_key and llm_url:
            from app.providers.llm import init_llm_provider
            init_llm_provider(
                api_key=llm_key,
                base_url=llm_url,
                model=llm_model,
                failure_threshold=settings.LLM_CIRCUIT_BREAKER_FAILURES,
                timeout_seconds=settings.LLM_CIRCUIT_BREAKER_TIMEOUT,
            )
        else:
            logger.warning("LLM provider not configured (LLM_API_KEY/LLM_BASE_URL empty)")

        # Embedding 初始化（优先本地模型，API 作为备选）
        from app.providers.embedding import init_embedding_provider, embedding_provider, NoOpEmbeddingProvider
        if settings.EMBEDDING_USE_LOCAL:
            logger.info(f"Trying local embedding model: {settings.EMBEDDING_LOCAL_MODEL}")
            emb = init_embedding_provider(use_local=True, local_model=settings.EMBEDDING_LOCAL_MODEL)
            # 测试本地模型是否真正可用
            test = emb.embed("test")
            if not test:
                logger.warning("Local embedding model not available, falling back to API...")
                if settings.EMBEDDING_API_KEY and settings.EMBEDDING_BASE_URL:
                    init_embedding_provider(
                        api_key=settings.EMBEDDING_API_KEY,
                        base_url=settings.EMBEDDING_BASE_URL,
                        model=settings.EMBEDDING_MODEL,
                    )
                    logger.info(f"Using API embedding model: {settings.EMBEDDING_MODEL}")
                else:
                    logger.warning("No embedding provider available, RAG disabled")
        elif settings.EMBEDDING_API_KEY and settings.EMBEDDING_BASE_URL:
            logger.info(f"Using API embedding model: {settings.EMBEDDING_MODEL}")
            init_embedding_provider(
                api_key=settings.EMBEDDING_API_KEY,
                base_url=settings.EMBEDDING_BASE_URL,
                model=settings.EMBEDDING_MODEL,
            )
        else:
            logger.warning("Embedding provider not configured, RAG disabled")

        # 向量库初始化（本地 SQLite 持久化，无需 ChromaDB 服务）
        from app.providers.vector_store import init_vector_store
        init_vector_store(use_local=True, local_db_path="./data/vectors.db")

    except Exception as e:
        logger.warning(f"Provider initialization skipped: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    db_ok = await check_db_connection()
    logger.info(f"Database connection: {'OK' if db_ok else 'FAILED'}")

    # 仅在 DEBUG 模式下自动建库建表（便于开发），生产环境请使用 Alembic 迁移
    if settings.DEBUG:
        if not db_ok:
            # 数据库不存在，先创建数据库
            logger.info("DEBUG mode: auto-creating database...")
            db_creation_url = (
                f"mysql+aiomysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
                f"@{settings.DB_HOST}:{settings.DB_PORT}"
            )
            temp_engine = create_async_engine(db_creation_url, echo=False)
            try:
                async with temp_engine.begin() as conn:
                    await conn.execute(text(
                        f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME} "
                        "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                    ))
                logger.info(f"Database '{settings.DB_NAME}' auto-created")
            finally:
                await temp_engine.dispose()

        logger.info("DEBUG mode: auto-creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables auto-created")

        # 老库补字段：create_all 不会向已存在的表添加新列
        # 先检查列是否存在，不存在才执行 ALTER TABLE（兼容老版本 MySQL）
        try:
            async with engine.connect() as conn:
                result = await conn.execute(text(
                    "SELECT COUNT(*) FROM information_schema.COLUMNS "
                    "WHERE TABLE_SCHEMA = :db AND TABLE_NAME = 'users' AND COLUMN_NAME = 'avatar_url'"
                ), {"db": settings.DB_NAME})
                exists = result.scalar() or 0

            if exists == 0:
                logger.info("Adding users.avatar_url column...")
                async with engine.begin() as conn:
                    await conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR(255) NULL"))
                logger.info("users.avatar_url column added")
            else:
                logger.info("users.avatar_url already exists, skipping migration")
        except Exception as e:
            logger.warning(f"users.avatar_url auto-migration failed: {e}")

        # 自动执行种子数据（部门、分类、默认管理员）
        seed_file = os.path.join(os.path.dirname(__file__), "..", "init_db.sql")
        if os.path.exists(seed_file):
            # 先检查是否已有种子数据，避免重复插入
            async with engine.connect() as conn:
                result = await conn.execute(
                    text("SELECT COUNT(*) FROM users WHERE user_id = 'user-admin-001'")
                )
                count = result.scalar()
            if count == 0:
                logger.info("DEBUG mode: seeding initial data...")
                with open(seed_file, "r", encoding="utf-8") as f:
                    sql_content = f.read()
                # 提取所有 INSERT 语句执行（忽略注释和 CREATE 等）
                for fragment in sql_content.split(";"):
                    stmt = fragment.strip()
                    insert_pos = stmt.upper().find("INSERT INTO")
                    if insert_pos >= 0:
                        stmt = stmt[insert_pos:]  # 去掉前面的注释
                        async with engine.begin() as conn:
                            await conn.execute(text(stmt))
                logger.info("Seed data applied (admin: admin001 / Admin@123)")
            else:
                logger.info("Seed data already exists, skipping")

            # 确保管理员密码哈希有效（修复旧数据中可能无效的hash）
            try:
                async with engine.connect() as conn:
                    result = await conn.execute(
                        text(
                            "SELECT password_hash FROM users WHERE user_id = 'user-admin-001'"
                        )
                    )
                    row = result.fetchone()
                if row:
                    import bcrypt
                    try:
                        valid = bcrypt.checkpw("Admin@123".encode(), row[0].encode())
                    except Exception:
                        valid = False
                    if not valid:
                        correct_hash = bcrypt.hashpw(
                            "Admin@123".encode(), bcrypt.gensalt(rounds=12)
                        ).decode()
                        async with engine.begin() as conn:
                            await conn.execute(
                                text(
                                    "UPDATE users SET password_hash = :pw "
                                    "WHERE user_id = 'user-admin-001'"
                                ),
                                {"pw": correct_hash},
                            )
                        logger.info("Admin password hash repaired")
            except Exception as e:
                logger.warning(f"Admin password hash check skipped: {e}")
    else:
        logger.info("Production mode: skipping auto-create, use Alembic migrations")

    try:
        await init_redis()
        logger.info("Redis connected")
    except Exception:
        logger.info("Redis not running, attempting auto-start...")
        if _start_redis():
            # 重试连接
            try:
                await init_redis()
                logger.info("Redis connected after auto-start")
            except Exception as e:
                logger.warning(f"Redis still unreachable after auto-start: {e}")
        else:
            logger.warning("Redis unavailable; rate limiting will be disabled")

    # 初始化 RAG 提供者（LLM/Embedding/ChromaDB）
    _init_providers()

    yield

    # 关闭时
    logger.info("Shutting down...")
    await close_redis()
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ── 中间件 ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(ClientPlatformMiddleware)

# ── 全局异常处理 ──
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# ── 注册路由 ──
api_v1_prefix = settings.API_V1_PREFIX
app.include_router(health_router, prefix=api_v1_prefix)
app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(documents_router, prefix=api_v1_prefix)
app.include_router(qa_router, prefix=api_v1_prefix)
app.include_router(admin_router, prefix=api_v1_prefix)
app.include_router(faqs_router, prefix=api_v1_prefix)
app.include_router(insights_router, prefix=api_v1_prefix)

# ── 上传文件静态目录（头像等）──
# 目录路径：backend/uploads，通过 /api/v1/uploads/* 对外访问；
# 前端 Vite dev 只代理 /api，所以要挂在 /api 前缀下才不跨域。
UPLOADS_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
(UPLOADS_DIR / "avatars").mkdir(parents=True, exist_ok=True)
app.mount(f"{api_v1_prefix}/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")


@app.get("/")
async def root():
    """根路径"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
