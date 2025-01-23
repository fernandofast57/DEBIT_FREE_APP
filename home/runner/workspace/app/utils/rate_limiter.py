
from typing import Dict, Optional
import time
import redis
import logging
from functools import wraps
from flask import request, current_app
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RateLimit:
    """Rate limit configuration"""
    requests: int
    window: int
    max_requests: Optional[int] = None
    window_size: Optional[int] = None

    def __post_init__(self):
        self.max_requests = self.max_requests or self.requests
        self.window_size = self.window_size or self.window

class RobustRateLimiter:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RobustRateLimiter, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized') or not self._initialized:
            try:
                self.redis = redis.Redis(
                    host=current_app.config.get('REDIS_HOST', 'localhost'),
                    port=current_app.config.get('REDIS_PORT', 6379),
                    db=0,
                    decode_responses=True
                )
                self._initialized = True
                self._local_cache: Dict[str, Dict] = {}
            except Exception as e:
                logger.error(f"Redis connection failed: {e}")
                self._local_cache: Dict[str, Dict] = {}

    def is_rate_limited(self, key: str, limit: RateLimit) -> bool:
        """
        Check if the request should be rate limited
        
        Args:
            key: Unique identifier for the rate limit
            limit: RateLimit configuration object
            
        Returns:
            bool: True if rate limited, False otherwise
        """
        try:
            return self._check_redis_limit(key, limit)
        except Exception as e:
            logger.warning(f"Falling back to local rate limiting: {e}")
            return self._check_local_limit(key, limit)

    def _check_redis_limit(self, key: str, limit: RateLimit) -> bool:
        try:
            current = int(time.time())
            pipeline = self.redis.pipeline()
            
            # Clean old requests
            pipeline.zremrangebyscore(key, 0, current - limit.window)
            
            # Count requests in window
            pipeline.zcard(key)
            
            # Add current request
            pipeline.zadd(key, {str(current): current})
            
            # Set expiry
            pipeline.expire(key, limit.window)
            
            _, request_count, *_ = pipeline.execute()
            
            return request_count > limit.requests
        except Exception as e:
            logger.error(f"Redis operation failed: {e}")
            raise

    def _check_local_limit(self, key: str, limit: RateLimit) -> bool:
        current = time.time()
        
        if key not in self._local_cache:
            self._local_cache[key] = []
            
        # Clean old requests
        self._local_cache[key] = [
            ts for ts in self._local_cache[key]
            if current - ts < limit.window
        ]
        
        # Check limit
        if len(self._local_cache[key]) >= limit.requests:
            return True
            
        # Add current request
        self._local_cache[key].append(current)
        return False

    def reset(self, key: str):
        """Reset rate limit for a key"""
        try:
            self.redis.delete(key)
        except Exception:
            self._local_cache.pop(key, None)

def rate_limit(limit_type: str = 'default'):
    """
    Decorator for rate limiting endpoints
    
    Args:
        limit_type: Type of rate limit to apply
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            limiter = RobustRateLimiter()
            key = f"{request.remote_addr}:{limit_type}"
            
            rate_limits = current_app.config.get('RATE_LIMITS', {
                'default': RateLimit(100, 60),
                'auth': RateLimit(5, 60),
                'api': RateLimit(60, 60)
            })
            
            limit = rate_limits.get(limit_type, rate_limits['default'])
            
            if limiter.is_rate_limited(key, limit):
                logger.warning(f"Rate limit exceeded for {key}")
                return {'error': 'Rate limit exceeded'}, 429
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
