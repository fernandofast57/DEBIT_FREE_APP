import redis.asyncio as redis
from typing import Any, Optional, Union, List
import pickle
import logging
import asyncio
from datetime import timedelta
from app.config.settings import Config

logger = logging.getLogger(__name__)

def get_redis_client():
    try:
        if hasattr(Config, 'REDIS_ENABLED') and Config.REDIS_ENABLED:
            return redis.Redis(
                host=getattr(Config, 'REDIS_HOST', '0.0.0.0'),
                port=getattr(Config, 'REDIS_PORT', 6379),
                decode_responses=False,
                socket_timeout=5,
                retry_on_timeout=True
            )
        return redis.Redis(
            host='0.0.0.0',
            port=6379,
            decode_responses=False,
            socket_timeout=5,
            retry_on_timeout=True
        )
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
        return None

class CacheManager:
    _instance = None

    def __new__(cls, redis_url: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, redis_url: str = None):
        if not hasattr(self, 'redis'):
            self.redis_url = redis_url or "redis://0.0.0.0:6379/0"
            self.redis = get_redis_client()
            self.default_ttl = 3600
            self._cache_hits = 0
            self._cache_misses = 0
            self._connection_retries = 3
            self._retry_delay = 1  # seconds

    async def ensure_connection(self):
        if self.redis is None or not self.redis.ping(): #This line is changed
            for attempt in range(self._connection_retries):
                try:
                    self.redis = redis.from_url(
                        self.redis_url,
                        encoding="utf-8",
                        decode_responses=False,
                        socket_timeout=5,
                        socket_connect_timeout=5,
                        retry_on_timeout=True,
                        health_check_interval=30
                    )
                    await self.redis.ping()
                    break
                except redis.ConnectionError as e:
                    if attempt == self._connection_retries - 1:
                        raise
                    await asyncio.sleep(self._retry_delay)

    async def get(self, key: str, default: Any = None) -> Optional[Any]:
        try:
            await self.ensure_connection()
            data = await self.redis.get(key)
            if data:
                self._cache_hits += 1
                return pickle.loads(data)
            self._cache_misses += 1
            return default
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return default

    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[Union[int, timedelta]] = None,
        nx: bool = False
    ) -> bool:
        try:
            await self.ensure_connection()
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
            await self.ensure_connection()
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