"""Redis 缓存与限流模块"""
import redis.asyncio as aioredis
from typing import Optional
from app.core.config import settings

redis_client: Optional[aioredis.Redis] = None


async def init_redis() -> aioredis.Redis:
    """初始化 Redis 连接"""
    global redis_client
    redis_client = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    return redis_client


async def close_redis():
    """关闭 Redis 连接"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


async def get_redis() -> aioredis.Redis:
    """获取 Redis 客户端实例"""
    if redis_client is None:
        await init_redis()
    return redis_client


async def check_redis_connection() -> bool:
    """检查 Redis 连接是否正常"""
    try:
        r = await get_redis()
        return await r.ping()
    except Exception:
        return False


async def rate_limit_check(key: str, max_requests: int, window_seconds: int = 60) -> bool:
    """使用滑动窗口限流，返回 True 表示允许"""
    r = await get_redis()
    current = await r.incr(key)
    if current == 1:
        await r.expire(key, window_seconds)
    return current <= max_requests
