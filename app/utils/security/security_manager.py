
from .rate_limiter import RobustRateLimiter
import logging

class SecurityManager:
    def __init__(self, app_name: str, redis_url: str = None):
        self.app_name = app_name
        self.rate_limiter = RateLimiter(redis_url)
        self.logger = logging.getLogger(app_name)
        
        self.setup_logging()
    
    def setup_logging(self):
        handler = logging.FileHandler(f'logs/{self.app_name}_security.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_security_event(self, event_type: str, details: dict):
        self.logger.info(f"Security event: {event_type}", extra={
            'event_type': event_type,
            'details': details
        })
