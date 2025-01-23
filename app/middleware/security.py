import time
from functools import wraps
from flask import request, abort, current_app, g
from typing import Dict, Optional
from redis import Redis
from app.utils.security.rate_limiter import RobustRateLimiter
from app.utils.security.jwt_manager import JWTManager

class SecurityMiddleware:
    def __init__(self, redis_client: Optional[Redis] = None, secret_key: str = None):
        self.redis = redis_client or Redis()
        self.rate_limiter = RobustRateLimiter()
        self.jwt_manager = JWTManager(secret_key=secret_key)
        self.rate_limits: Dict[str, int] = {
            'default': 100,    # requests per minute
            'auth': 5,         # login attempts per minute
            'api': 60,         # api calls per minute
            'transform': 10,   # transformation requests per minute
            'sensitive': 3     # sensitive operations per minute
        }
        self._max_retries = 3 # Added max retry attempts
        self._retry_count = 0 # Added retry counter

    def require_auth(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                abort(401, description="No authorization token provided")

            try:
                payload = self.jwt_manager.verify_token(token)
                g.user_id = payload['sub']
                g.user_role = payload.get('role', 'user')
            except Exception as e:
                abort(401, description=str(e))

            return f(*args, **kwargs)
        return decorated

    def rate_limit(self, limit_type='default'):
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                key = f"{request.remote_addr}:{limit_type}"
                if self._retry_count >= self._max_retries:
                    self._retry_count = 0
                    abort(429, description="Rate limit exceeded, too many retries") #Abort after max retries
                if self.rate_limiter.is_rate_limited(key, self.rate_limits[limit_type]):
                    self._retry_count += 1
                    time.sleep(1) # Introduce delay before retrying
                    return decorated(*args, **kwargs) #Retry the function
                self._retry_count = 0
                return f(*args, **kwargs)
            return decorated
        return decorator

    def require_role(self, required_role):
        def decorator(f):
            @wraps(f)
            @self.require_auth
            def decorated(*args, **kwargs):
                if g.user_role != required_role:
                    abort(403, description="Insufficient permissions")
                return f(*args, **kwargs)
            return decorated
        return decorator

security = SecurityMiddleware()