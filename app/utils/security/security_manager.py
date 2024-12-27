import os
from flask import request, current_app
from functools import wraps
import time
from typing import Dict, List
import logging

class SecurityManager:
    def __init__(self):
        self.rate_limit: Dict[str, List[float]] = {}
        self.request_limit = 5
        self.time_window = 60
        log_dir = "logs"
        log_file = os.path.join(log_dir, "security.log")
        os.makedirs(log_dir, exist_ok=True) # Ensure logs directory exists

        logging.basicConfig(filename=log_file, level=logging.WARNING,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('security')
        
    def log_security_event(self, event_type: str, event_data: dict):
        """Log security events while removing sensitive data"""
        # Remove sensitive fields
        sanitized_data = event_data.copy()
        sensitive_fields = ['password', 'api_key', 'secret', 'token']
        for field in sensitive_fields:
            if field in sanitized_data:
                sanitized_data[field] = '[REDACTED]'
        
        self.logger.warning(f"Security event {event_type}: {sanitized_data}")
        
    def require_rate_limit(self, func):
        @wraps(func)
        def decorated(*args, **kwargs):
            ip = request.remote_addr
            current_time = time.time()
            
            if ip not in self.rate_limit:
                self.rate_limit[ip] = []
            
            # Clean old requests
            self.rate_limit[ip] = [
                req_time for req_time in self.rate_limit[ip]
                if current_time - req_time < self.time_window
            ]
            
            if len(self.rate_limit[ip]) >= self.request_limit:
                current_app.logger.warning(f"Rate limit exceeded for IP: {ip}")
                return {"error": "Too many requests"}, 429
                
            self.rate_limit[ip].append(current_time)
            return func(*args, **kwargs)
        return decorated

security_manager = SecurityManager()