import os
import logging
from flask import request, current_app
from functools import wraps
import time
from typing import Dict, List
import re
import json
from datetime import datetime

class SecurityManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.permission_cache = {}
        self.rate_limit: Dict[str, List[float]] = {}
        self.request_limit = 5
        self.time_window = 60
        log_dir = "logs"
        log_file = os.path.join(log_dir, "security.log")
        os.makedirs(log_dir, exist_ok=True)

        logging.basicConfig(filename=log_file, level=logging.WARNING,
                          format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('security')
    
    def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        cache_key = f"{user_id}:{resource}:{action}"
        if cache_key in self.permission_cache:
            return self.permission_cache[cache_key]
            
        # Get user roles and permissions
        user_roles = self._get_user_roles(user_id)
        has_permission = any(self._role_has_permission(role, resource, action) 
                           for role in user_roles)
                           
        # Cache the result
        self.permission_cache[cache_key] = has_permission
        return has_permission
    
    def _get_user_roles(self, user_id: str) -> list:
        # TODO: Implement role fetching from database
        return ['user']  # Default role
        
    def _role_has_permission(self, role: str, resource: str, action: str) -> bool:
        permissions = {
            'admin': {'all': ['read', 'write', 'delete']},
            'manager': {
                'transactions': ['read', 'write'],
                'users': ['read']
            },
            'user': {
                'transactions': ['read'],
                'profile': ['read', 'write']
            }
        }
        
        role_perms = permissions.get(role, {})
        resource_perms = role_perms.get(resource, [])
        return action in resource_perms or 'all' in role_perms
        
    def log_security_event(self, event_type: str, event_data: dict):
        sanitized_data = self._sanitize_sensitive_data(event_data)
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': event_type,
            'data': sanitized_data
        }
        
        with open('logs/security.log', 'a') as f:
            json.dump(log_entry, f)
            f.write('\n')

    def _sanitize_sensitive_data(self, event_data: dict):
        sanitized_data = event_data.copy()
        sensitive_fields = ['password', 'api_key', 'secret', 'token']
        for field in sensitive_fields:
            if field in sanitized_data:
                sanitized_data[field] = '[REDACTED]'
        return sanitized_data

    @staticmethod
    def validate_address(address):
        """Validate Ethereum address format"""
        if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
            return False
        return True

    @staticmethod
    def sanitize_input(data):
        """Sanitize user input"""
        def clean_string(s):
            # Remove common SQL injection patterns
            sql_patterns = ["DROP TABLE", "UNION SELECT", "--", ";", "DELETE FROM", "INSERT INTO", "UPDATE"]
            # Remove XSS patterns
            xss_patterns = ["<script>", "</script>", "javascript:", "<img", "onerror="]
            # Remove path traversal
            path_patterns = ["../", "..\\", "/..", "\\..", "../../../../", "..../"]
            
            result = s
            for pattern in sql_patterns + xss_patterns + path_patterns:
                result = result.replace(pattern, "")
            return result.strip()

        if isinstance(data, dict):
            return {k: SecurityManager.sanitize_input(v) for k, v in data.items()}
        if isinstance(data, str):
            return clean_string(data)
        return data

    def require_rate_limit(self, func):
        @wraps(func)
        def decorated(*args, **kwargs):
            ip = request.remote_addr
            current_time = time.time()
            
            if ip not in self.rate_limit:
                self.rate_limit[ip] = []
            
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