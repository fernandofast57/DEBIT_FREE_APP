
from datetime import datetime, timedelta
from typing import Optional, Dict
import jwt
from app.utils.security.security_manager import SecurityManager
from app.models.models import db

class AuthManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.security = SecurityManager()
    
    def generate_token(self, user_id: int, device_id: str) -> str:
        payload = {
            'user_id': user_id,
            'device_id': device_id,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            if self.security.is_token_revoked(token):
                return None
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def revoke_token(self, token: str) -> bool:
        return self.security.revoke_token(token)
    
    def is_valid_device(self, user_id: int, device_id: str) -> bool:
        return self.security.validate_device(user_id, device_id)
