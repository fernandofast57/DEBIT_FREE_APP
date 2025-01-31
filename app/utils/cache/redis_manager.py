import redis.asyncio as redis
from typing import Any, Optional, Union, List
import pickle
import logging
import asyncio
from datetime import timedelta
from app.config.settings import Config
from app.config.redis import RedisConfig
from app.config.constants import CACHE_TIMEOUT # Added import

logger = logging.getLogger(__name__)

class DictCache:
    def __init__(self):
        self._cache = {}

    async def get(self, key):
        return self._cache.get(key)

    async def set(self, key, value, ex=None):
        self._cache[key] = value
        return True

    async def delete(self, *keys):
        count = 0
        for key in keys:
            if key in self._cache:
                del self._cache[key]
                count += 1
        return count

    async def ping(self):
        return True

async def get_redis_client():
    try:
        redis_client = redis.Redis(
            host=getattr(Config, 'REDIS_HOST', 'localhost'), #default to localhost
            port=getattr(Config, 'REDIS_PORT', 6379),
            db=getattr(Config, 'REDIS_DB', 0), #Added db for configuration
            decode_responses=True,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
            socket_connect_timeout=2 #Added connect timeout
        )
        await redis_client.ping()
        return redis_client
    except (redis.ConnectionError, ConnectionError) as e: #Handle both exception types
        logger.warning(f"Redis connection failed: {e}, using fallback cache")
        return DictCache()
    except Exception as e:
        logger.error(f"Unexpected error connecting to Redis: {e}, using fallback cache")
        return DictCache()


class GestoreCache:
    _instance = None
    TENTATIVI_MAX = 3
    RITARDO_RETRY = 1

    def __new__(cls, redis_url: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, redis_url: str = None):
        self.config = RedisConfig(redis_url)
        self.redis = None
        self.initialized = False
        self.default_ttl = self.config.CACHE_TIMEOUT # Changed to CACHE_TIMEOUT

    async def initialize(self):
        if not self.initialized:
            await self._init_redis()
            self.initialized = True

    CACHE_TTL = 3600  # Allineato con MetricsType
    MAX_RETRY_ATTEMPTS = 3  # Allineato con SecurityLevel
    RETRY_INTERVAL = 1  # Allineato con OperationType

    async def _init_redis(self):
        self.redis = await get_redis_client()
        self.default_ttl = CACHE_TIMEOUT # Changed to CACHE_TIMEOUT
        self._cache_hits = 0
        self._cache_misses = 0
        self._connection_retries = self.TENTATIVI_MAX
        self._retry_delay = self.RITARDO_RETRY  # seconds

    async def ensure_connection(self):
        if self.redis is None or not await self.redis.ping(): # await ping
            for attempt in range(self._connection_retries):
                try:
                    self.redis = await get_redis_client() #Use the function to handle potential errors
                    if self.redis and await self.redis.ping():
                        break
                    else:
                        await asyncio.sleep(self._retry_delay)
                except Exception as e:
                    if attempt == self._connection_retries - 1:
                        logger.error(f"Failed to connect to Redis after multiple retries: {e}")
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
                ex=ttl or self.default_ttl, #Using default_ttl
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

    async def clear_cache(self):
        """Clear all cache data"""
        try:
            if self.redis:
                await self.redis.flushdb()
            self._cache_hits = 0
            self._cache_misses = 0
            logger.info("Cache cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            raise

gestore_cache = GestoreCache()
cache_manager = gestore_cache  # Create alias for consistency