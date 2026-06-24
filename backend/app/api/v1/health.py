"""健康检查接口"""
from fastapi import APIRouter
from app.core.database import check_db_connection
from app.core.redis import check_redis_connection

router = APIRouter(tags=["系统"])


@router.get("/health")
async def health_check():
    """系统健康检查"""
    db_ok = await check_db_connection()
    redis_ok = await check_redis_connection()
    return {
        "code": 0,
        "message": "success",
        "data": {
            "status": "healthy" if (db_ok) else "degraded",
            "database": "connected" if db_ok else "disconnected",
            "redis": "connected" if redis_ok else "disconnected",
            "version": "1.0.0",
        },
    }
