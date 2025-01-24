
from typing import Optional
import redis.asyncio as redis
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

class RedisConfig:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or "redis://0.0.0.0:6379/0"
        
    async def get_connection(self) -> redis.Redis:
        try:
            return redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        except Exception as e:
            logger.error(f"Redis connection error: {e}")
            raise
