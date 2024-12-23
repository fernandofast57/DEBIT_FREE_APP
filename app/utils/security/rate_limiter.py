
from collections import defaultdict
import time
from typing import Dict, Tuple
import redis
import functools
from app.utils.logging_config import logger

class RobustRateLimiter:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.window_size = 60  # 1 minute window
        self.max_requests = 100  # max requests per window
        
    def is_rate_limited(self, key: str) -> bool:
        pipe = self.redis.pipeline()
        now = time.time()
        window_start = now - self.window_size
        
        try:
            # Remove old requests
            pipe.zremrangebyscore(key, 0, window_start)
            # Count requests in current window
            pipe.zcard(key)
            # Add new request
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, self.window_size)
            
            _, request_count, *_ = pipe.execute()
            
            return request_count > self.max_requests
        except redis.RedisError as e:
            logger.error(f"Redis error in rate limiter: {e}")
            return False

def rate_limit(max_requests: int = 100, window: int = 60):
    def decorator(f):
        requests = defaultdict(list)
        
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            now = time.time()
            key = f.__name__
            
            # Clean old requests
            requests[key] = [req_time for req_time in requests[key] 
                           if now - req_time < window]
            
            if len(requests[key]) >= max_requests:
                return {"error": "Rate limit exceeded"}, 429
                
            requests[key].append(now)
            return f(*args, **kwargs)
            
        return wrapped
    return decorator
