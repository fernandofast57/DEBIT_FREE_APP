
import time
from typing import Dict, Tuple
from collections import defaultdict
from dataclasses import dataclass
import redis
from flask import request
from functools import wraps

@dataclass
class RateLimit:
    requests: int
    window: int
    by_ip: bool = True
    by_user: bool = True

class RateLimiter:
    def __init__(self, redis_url: str = None):
        self.redis = redis.from_url(redis_url) if redis_url else None
        self.local_storage: Dict[str, Dict[float, int]] = defaultdict(dict)
    
    def _get_key(self, by_ip: bool, by_user: bool) -> str:
        key_parts = []
        if by_ip:
            key_parts.append(request.remote_addr)
        if by_user and hasattr(request, 'user'):
            key_parts.append(str(request.user.id))
        return ':'.join(key_parts) if key_parts else 'global'

    def is_allowed(self, key: str, limit: RateLimit) -> bool:
        current = time.time()
        window_start = current - limit.window

        if self.redis:
            return self._check_redis(key, limit, current, window_start)
        return self._check_local(key, limit, current, window_start)

    def _check_local(self, key: str, limit: RateLimit, current: float, window_start: float) -> bool:
        self.local_storage[key] = {
            ts: count for ts, count in self.local_storage[key].items()
            if ts > window_start
        }
        
        total_requests = sum(self.local_storage[key].values())
        if total_requests >= limit.requests:
            return False
            
        self.local_storage[key][current] = 1
        return True

    def _check_redis(self, key: str, limit: RateLimit, current: float, window_start: float) -> bool:
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zadd(key, {str(current): 1})
        pipe.zcard(key)
        pipe.expire(key, limit.window)
        _, _, total_requests, _ = pipe.execute()
        
        return total_requests <= limit.requests

def rate_limit(requests: int, window: int, by_ip: bool = True, by_user: bool = True):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            limit = RateLimit(requests, window, by_ip, by_user)
            key = request.rate_limiter._get_key(by_ip, by_user)
            
            if not request.rate_limiter.is_allowed(key, limit):
                return {'error': 'Rate limit exceeded'}, 429
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
