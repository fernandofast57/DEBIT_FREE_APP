import time
from functools import wraps
from flask import request, abort, current_app
from typing import Dict, Optional
from redis import Redis
from app.utils.security.robust_rate_limiter import RobustRateLimiter
from app.utils.security import JWTManager
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    def __init__(self, redis_client: Optional[Redis] = None, secret_key: str = None):
        self.redis = redis_client or Redis()
        self.jwt_manager = JWTManager(secret_key=secret_key)

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
            def decorated_function(*args, **kwargs):
                limiter = RobustRateLimiter()
                key = f"{request.remote_addr}:{limit_type}"

                # Get limits from config according to standards
                limits = current_app.config.get('RATE_LIMITS', {
                    'default': {'max_requests': 50, 'window': 60},
                    'auth': {'max_requests': 5, 'window': 60},
                    'api': {'max_requests': 50, 'window': 60}
                })

                limit = limits.get(limit_type, limits['default'])

                if limiter.is_rate_limited(key, limit['max_requests'], limit['window']):
                    logger.warning(f"Rate limit exceeded for {key}")
                    return {'error': 'Rate limit exceeded'}, 429

                return f(*args, **kwargs)
            return decorated_function
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