
from flask import request
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict
import threading

class RateLimiter:
    def __init__(self, max_requests=100, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self._cleanup_lock = threading.Lock()

    def is_rate_limited(self, key: str) -> bool:
        self._cleanup_old_requests()
        requests = self.requests[key]
        return len(requests) >= self.max_requests

    def _cleanup_old_requests(self):
        with self._cleanup_lock:
            current = datetime.now()
            for key in list(self.requests.keys()):
                self.requests[key] = [
                    req_time for req_time in self.requests[key]
                    if current - req_time < timedelta(seconds=self.window_seconds)
                ]

rate_limiter = RateLimiter()

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        key = f"{request.remote_addr}:{f.__name__}"
        if rate_limiter.is_rate_limited(key):
            return {'error': 'Rate limit exceeded'}, 429
        rate_limiter.requests[key].append(datetime.now())
        return f(*args, **kwargs)
    return decorated_function
