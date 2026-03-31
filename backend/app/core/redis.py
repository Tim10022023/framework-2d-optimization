import redis.asyncio as redis
from app.core.config import settings

_redis_client: redis.Redis | None = None

async def init_redis():
    global _redis_client
    try:
        client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        await client.ping()
        _redis_client = client
        print("Redis connected successfully.")
    except Exception as e:
        print(f"Redis connection failed: {e}")
        _redis_client = None

def get_redis():
    return _redis_client

async def close_redis():
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
