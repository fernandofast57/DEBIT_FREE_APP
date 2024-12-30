import time
from functools import wraps
from flask import request, abort, current_app
from typing import Dict, Optional
from redis import Redis

class SecurityMiddleware:
    def __init__(self, redis_client: Optional[Redis] = None):
        self.redis = redis_client or Redis()
        self.rate_limits: Dict[str, int] = {
            'default': 100,  # requests per minute
            'auth': 5,      # login attempts per minute
            'api': 60       # api calls per minute
        }

    def require_auth(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                abort(401)
            try:
                if not current_app.auth_service.verify_token(auth_header):
                    abort(401)
            except Exception:
                abort(401)
            return f(*args, **kwargs)
        return decorated

    def rate_limit(self, limit_type='default'):
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                key = f"{request.remote_addr}:{limit_type}"
                current = int(self.redis.get(key) or 0)
                
                if current >= self.rate_limits[limit_type]:
                    abort(429)
                
                pipe = self.redis.pipeline()
                pipe.incr(key)
                pipe.expire(key, 60)
                pipe.execute()
                
                return f(*args, **kwargs)
            return decorated
        return decorator

security = SecurityMiddleware()