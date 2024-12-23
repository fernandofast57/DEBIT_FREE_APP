
from .rate_limiter import RobustRateLimiter
import logging
from app.utils.logging_config import APP_NAME

class SecurityManager:
    def __init__(self, app_name: str = APP_NAME, redis_url: str = None):
        self.app_name = APP_NAME
        default_redis_url = "redis://localhost:6379/0"
        self.rate_limiter = RobustRateLimiter(redis_url or default_redis_url)
        self.logger = logging.getLogger(APP_NAME)
        
        self.setup_logging()
    
    def setup_logging(self):
        handler = logging.FileHandler(f'logs/{self.app_name}_security.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
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
