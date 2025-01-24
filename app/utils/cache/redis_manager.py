
import redis.asyncio as redis
from typing import Any, Optional, Union, List
import pickle
import logging
import asyncio
from datetime import timedelta

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, redis_url: str = None):
        self.redis = redis.from_url(redis_url or "redis://0.0.0.0:6379/0")
        self.default_ttl = 3600
        self._cache_hits = 0
        self._cache_misses = 0

    async def get(self, key: str, default: Any = None) -> Optional[Any]:
        try:
            data = await self.redis.get(key)
            if data:
                self._cache_hits += 1
                return pickle.loads(data)
            self._cache_misses += 1
            return default
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return default

    async def mget(self, keys: List[str]) -> List[Optional[Any]]:
        try:
            values = await self.redis.mget(keys)
            return [pickle.loads(v) if v else None for v in values]
        except Exception as e:
            logger.error(f"Cache mget error: {str(e)}")
            return [None] * len(keys)

    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[Union[int, timedelta]] = None,
        nx: bool = False
    ) -> bool:
        try:
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            
            return await self.redis.set(
                key,
                pickle.dumps(value),
                ex=ttl or self.default_ttl,
                nx=nx
            )
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache pattern deletion error: {str(e)}")
            return 0

    async def get_cache_stats(self) -> dict:
        return {
            'hits': self._cache_hits,
            'misses': self._cache_misses,
            'hit_ratio': self._cache_hits / (self._cache_hits + self._cache_misses) if (self._cache_hits + self._cache_misses) > 0 else 0
        }

cache_manager = CacheManager()
