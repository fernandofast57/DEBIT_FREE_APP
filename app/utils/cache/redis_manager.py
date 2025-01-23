
from typing import Any, Optional, Union, List
import redis.asyncio as redis
import json
import logging
from datetime import timedelta
import pickle

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, redis_url: str = None):
        self.redis = redis.from_url(redis_url or "redis://localhost:6379/0")
        self.default_ttl = 3600

    async def get(self, key: str, default: Any = None) -> Optional[Any]:
        try:
            data = await self.redis.get(key)
            return pickle.loads(data) if data else default
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return default

    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        try:
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
                
            return await self.redis.setex(
                key,
                ttl or self.default_ttl,
                pickle.dumps(value)
            )
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False

    async def delete(self, *keys: str) -> int:
        try:
            return await self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return 0

    async def invalidate_pattern(self, pattern: str) -> int:
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache invalidation error: {str(e)}")
            return 0

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error: {str(e)}")
            return None

cache_manager = CacheManager()
