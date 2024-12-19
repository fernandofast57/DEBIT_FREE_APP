
import redis
from typing import Optional, Any
import json
import logging

class RedisManager:
    """Gestore Redis con fallback locale"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url
        self.client = self._create_client()
        self.local_cache = {}
        self.logger = logging.getLogger('redis')
        self._setup_logging()

    def _setup_logging(self):
        handler = logging.FileHandler('logs/redis.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def _create_client(self) -> Optional[redis.Redis]:
        if not self.redis_url:
            return None
        try:
            client = redis.from_url(self.redis_url)
            client.ping()
            return client
        except redis.RedisError as e:
            self.logger.error(f"Failed to connect to Redis: {str(e)}")
            return None

    def get(self, key: str, default: Any = None) -> Any:
        try:
            if self.client:
                value = self.client.get(key)
                if value:
                    return json.loads(value)
            return self.local_cache.get(key, default)
        except (redis.RedisError, json.JSONDecodeError) as e:
            self.logger.error(f"Redis get error: {str(e)}")
            return self.local_cache.get(key, default)

    def set(self, key: str, value: Any, expire: int = None):
        try:
            serialized = json.dumps(value)
            if self.client:
                if expire:
                    self.client.setex(key, expire, serialized)
                else:
                    self.client.set(key, serialized)
            self.local_cache[key] = value
        except (redis.RedisError, json.JSONDecodeError) as e:
            self.logger.error(f"Redis set error: {str(e)}")
            self.local_cache[key] = value
