
import time
from collections import defaultdict
from typing import Dict, Tuple
from functools import wraps
from flask import request

class RobustRateLimiter:
    def __init__(self, redis_url: str = None):
        """Redis-backed rate limiting component"""
        self.redis_url = redis_url
        self.local_storage: Dict[str, Dict[str, Tuple[int, float]]] = defaultdict(dict)
        self.window_size = 60  # 1 minute window
        self.max_requests = 50  # 50 requests per minute
        
    def is_rate_limited(self, key: str, max_requests: int = None, window_size: int = None) -> bool:
        """Check if request should be rate limited"""
        current = time.time()
        window_size = window_size or self.window_size
        max_reqs = max_requests or self.max_requests
        
        if key not in self.local_storage:
            self.local_storage[key] = {'count': 1, 'window_start': current}
            return False
            
        window_start = self.local_storage[key]['window_start']
        if current - window_start > window_size:
            self.local_storage[key] = {'count': 1, 'window_start': current}
            return False
            
        self.local_storage[key]['count'] += 1
        return self.local_storage[key]['count'] > max_reqs

def rate_limit(max_requests: int = 100, window_size: int = 60):
    """Decorator for endpoint-specific rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            limiter = RobustRateLimiter()
            key = f"{request.remote_addr}:{f.__name__}"
            if limiter.is_rate_limited(key, max_requests, window_size):
                return {'error': 'Rate limit exceeded'}, 429
            return f(*args, **kwargs)
        return decorated_function
    return decorator
