
from typing import Any, Optional
import redis.asyncio as redis
import json
from app.utils.logging_config import logger

class RedisManager:
    def __init__(self, redis_url: str = None):
        self.redis = redis.from_url(redis_url or "redis://localhost:6379/0")
        self.default_ttl = 3600  # 1 hour
        
    async def get(self, key: str) -> Optional[Any]:
        try:
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
            
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        try:
            return await self.redis.setex(
                key,
                ttl or self.default_ttl,
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
            
    async def invalidate(self, pattern: str) -> None:
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
