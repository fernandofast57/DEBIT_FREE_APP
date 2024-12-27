
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
