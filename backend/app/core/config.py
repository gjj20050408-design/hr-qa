"""核心配置管理模块"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置，支持从环境变量和 .env 文件加载"""

    # 应用基础配置
    APP_NAME: str = "HR政策智能问答系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    CONDA_ENV_NAME: str = "hr-qa"  # 仅脚本使用
    CONDA_BASE_PATH: str = ""  # 仅脚本使用

    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "hr_policy_qa"
    DATABASE_URL: Optional[str] = None

    @property
    def db_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SERVER_PATH: Optional[str] = None  # 仅脚本使用，启动本地 Redis 时读取

    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # JWT 配置
    JWT_SECRET_KEY: str = "change-me-in-production-use-a-strong-random-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 安全配置
    BCRYPT_ROUNDS: int = 12
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30
    SESSION_IDLE_TIMEOUT_MINUTES: int = 30

    # 限流配置
    RATE_LIMIT_QNA_PER_MINUTE: int = 20
    RATE_LIMIT_SEARCH_PER_MINUTE: int = 30

    # 文件上传
    MAX_UPLOAD_SIZE_MB: int = 20
    UPLOAD_DIR: str = "./uploads"

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    @property
    def celery_broker(self) -> str:
        return self.CELERY_BROKER_URL or self.redis_url

    @property
    def celery_backend(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.redis_url

    # 问答策略链阈值
    FAQ_SIMILARITY_MIN: float = 0.70
    SEARCH_MAX_RESULTS: int = 20
    RAG_TOP_K_RETRIEVAL: int = 10
    RAG_TOP_N_PROMPT: int = 5
    RAG_CHUNK_TOKEN_SIZE: int = 500
    LLM_TIMEOUT_SECONDS: int = 60
    LLM_CIRCUIT_BREAKER_FAILURES: int = 5
    LLM_CIRCUIT_BREAKER_TIMEOUT: int = 30

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:80"]

    # Redis 自动启动配置（Windows 本地开发）
    REDIS_AUTO_START: bool = False  # 设为 True 以在启动时自动拉起 Redis
    REDIS_SERVER_PATH: str = "redis-server.exe"  # redis-server 路径，支持 PATH 中的命令

    # 日志
    LOG_LEVEL: str = "DEBUG"

    # LLM / Embedding / ChromaDB 配置
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None
    LLM_MODEL: str = "qwen-turbo"
    EMBEDDING_API_KEY: Optional[str] = None
    EMBEDDING_BASE_URL: Optional[str] = None
    EMBEDDING_MODEL: str = "text-embedding-v3"
    # 本地 Embedding 配置（use_local=true 时使用本地模型，无需 API Key）
    EMBEDDING_USE_LOCAL: bool = False
    EMBEDDING_LOCAL_MODEL: str = "BAAI/bge-small-zh-v1.5"
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
