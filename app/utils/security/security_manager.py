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

    def sanitize_input(self, data):
        if isinstance(data, dict):
            return {k: self.sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_input(x) for x in data]
        elif isinstance(data, str):
            # Sanitize string
            sanitized = self._remove_sql_injection(data)
            sanitized = self._remove_xss(sanitized)
            sanitized = self._remove_path_traversal(sanitized)
            sanitized = self._validate_special_chars(sanitized)
            sanitized = self._check_length_limits(sanitized)
            sanitized = self._validate_encoding(sanitized)
            return sanitized
        return data

    def _remove_sql_injection(self, data: str) -> str:
        #This is a placeholder, needs robust implementation.
        return data

    def _remove_xss(self, data: str) -> str:
        #This is a placeholder, needs robust implementation.
        return data

    def _remove_path_traversal(self, data: str) -> str:
        #This is a placeholder, needs robust implementation.
        return data

    def _validate_special_chars(self, data: str) -> str:
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.,@() ")
        if not all(c in allowed_chars for c in data):
            return ''.join(c for c in data if c in allowed_chars)
        return data

    def _check_length_limits(self, data: str) -> str:
        MAX_LENGTH = 1000
        return data[:MAX_LENGTH] if len(data) > MAX_LENGTH else data

    def _validate_encoding(self, data: str) -> str:
        try:
            return data.encode('utf-8').decode('utf-8')
        except UnicodeError:
            return ''

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