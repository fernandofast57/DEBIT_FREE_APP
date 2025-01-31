
import logging
from typing import Optional
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

class RedisConfig:
    CACHE_HOST = 'localhost'
    CACHE_PORT = 6379
    CACHE_DB = 0
    CACHE_TIMEOUT = 3600  # Allineato con MetricsType.CACHE_TIMEOUT
    CACHE_PREFIX = 'gold_investment'
    MAX_RETRY_ATTEMPTS = 3  # Allineato con SecurityLevel
    RETRY_INTERVAL = 1  # Allineato con OperationType
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or f"redis://{self.CACHE_HOST}:{self.CACHE_PORT}/{self.CACHE_DB}"
        self.initialized = False

    def get_connection_url(self) -> str:
        return self.redis_url
