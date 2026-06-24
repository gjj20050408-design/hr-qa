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
    """滑动窗口限流器（基于 Sorted Set 实现），返回 True 表示允许。

    使用毫秒级时间戳作为 score，每次请求：
    1. 移除窗口外的旧记录
    2. 检查当前窗口内请求数
    3. 未超限则添加新记录并返回 True
    """
    import time
    r = await get_redis()
    now_ms = int(time.time() * 1000)
    window_start = now_ms - (window_seconds * 1000)

    # Lua 脚本保证原子性：清理过期记录 → 计数 → 判断
    lua_script = """
    local key = KEYS[1]
    local now = tonumber(ARGV[1])
    local window_start = tonumber(ARGV[2])
    local max_requests = tonumber(ARGV[3])
    local window_seconds = tonumber(ARGV[4])

    -- 1. 移除窗口外的记录
    redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)

    -- 2. 获取当前窗口内的请求数
    local current = redis.call('ZCARD', key)

    -- 3. 判断是否允许
    if current < max_requests then
        -- 使用纳秒级随机后缀避免同毫秒冲突
        local member = now .. ':' .. redis.call('INCR', key .. ':counter')
        redis.call('ZADD', key, now, member)
        redis.call('EXPIRE', key, window_seconds * 2)
        return 1
    else
        return 0
    end
    """
    result = await r.eval(lua_script, 1, key, now_ms, window_start, max_requests, window_seconds)
    return bool(result)
