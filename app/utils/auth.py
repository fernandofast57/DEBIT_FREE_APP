
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict

class AuthManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        
    def generate_token(self, user_id: int, device_id: str) -> str:
        payload = {
            'user_id': user_id,
            'device_id': device_id,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
        
    def verify_token(self, token: str) -> Optional[Dict]:
        try:
            return jwt.decode(token, self.secret_key, algorithms=['HS256'])
        except:
            return None
