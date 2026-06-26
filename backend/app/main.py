"""FastAPI 主应用入口"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# 日志配置
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


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
    else:
        logger.info("Production mode: skipping auto-create, use Alembic migrations")

    try:
        await init_redis()
        logger.info("Redis connected")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")

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
