
from typing import Any, Optional
import redis
import json
from app.utils.logging_config import logger

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.default_ttl = 3600  # 1 hour
        
    async def get(self, key: str) -> Optional[Any]:
        try:
            data = self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
            
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        try:
            return self.redis.setex(
                key,
                ttl or self.default_ttl,
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
            
    async def invalidate(self, pattern: str) -> None:
        try:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
