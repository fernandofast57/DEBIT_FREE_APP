
from functools import wraps
from flask import request, current_app
from app.utils.robust_rate_limiter import RobustRateLimiter, RateLimit
import logging

logger = logging.getLogger(__name__)

def rate_limit(limit_type='default'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            limiter = RobustRateLimiter()
            key = f"{request.remote_addr}:{f.__name__}"
            
            limits = current_app.config.get('RATE_LIMITS', {
                'default': RateLimit(requests=50, window=60),
                'auth': RateLimit(requests=5, window=60),
                'api': RateLimit(requests=50, window=60)
            })
            
            limit = limits.get(limit_type, limits['default'])
            
            if limiter.is_rate_limited(key, limit):
                logger.warning(f"Rate limit exceeded for {key}")
                return {'error': 'Rate limit exceeded'}, 429
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
