
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from app.utils.logging_config import APP_NAME
from .rate_limiter import RobustRateLimiter

class SecurityManager:
    """Manages security operations and rate limiting"""
    def __init__(self, app=None, app_name: str = APP_NAME, redis_url: str = None):
        self.app_name = APP_NAME
        self.limiter = None
        if app:
            self.init_app(app)
            
        try:
            self.rate_limiter = RobustRateLimiter(redis_url)
        except Exception as e:
            self.logger = logging.getLogger(APP_NAME)
            self.logger.warning(f"Failed to initialize rate limiter: {e}. Using local storage.")
            self.rate_limiter = RobustRateLimiter(None)
        
        self.logger = logging.getLogger(APP_NAME)
        self.setup_logging()
    
    def init_app(self, app):
        """Initialize Flask-Limiter with the application"""
        self.limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=["100 per day", "10 per minute"],
            storage_uri=app.config.get('REDIS_URL', 'memory://')
        )
        return self.limiter
    
    def setup_logging(self):
        handler = logging.FileHandler(f'logs/{self.app_name}_security.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(statuscode)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_security_event(self, event_type: str, details: dict):
        valid_statuses = ['to_be_verified', 'verified', 'available', 'reserved', 'distributed']
        if 'status' in details and details['status'] not in valid_statuses:
            raise ValueError(f"Invalid status code: {details['status']}")
            
        self.logger.info(f"Security event: {event_type}", extra={
            'event_type': event_type,
            'details': details
        })

    def get_limiter(self):
        """Get the Flask-Limiter instance"""
        if not self.limiter:
            raise RuntimeError("Limiter not initialized. Call init_app first.")
        return self.limiter
