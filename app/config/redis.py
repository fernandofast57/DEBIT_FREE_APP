
from typing import Optional
import redis.asyncio as redis
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

class RedisConfig:
    DEFAULT_HOST = '0.0.0.0'
    DEFAULT_PORT = 6379
    DEFAULT_DB = 0
    DEFAULT_TIMEOUT = 5
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or f"redis://{self.DEFAULT_HOST}:{self.DEFAULT_PORT}/{self.DEFAULT_DB}"
        
    async def get_connection(self) -> redis.Redis:
        try:
            return redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=self.DEFAULT_TIMEOUT,
                retry_on_timeout=True,
                health_check_interval=30
            )
        except Exception as e:
            logger.error(f"Redis connection error: {str(e)}")
            raise
