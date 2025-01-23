
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional
from flask import current_app

class JWTManager:
    def __init__(self, secret_key: str = None, token_expire_hours: int = 24):
        self.secret_key = secret_key or 'default-secret-key'
        self.token_expire_hours = token_expire_hours

    def create_token(self, user_id: int, role: str = 'user') -> str:
        payload = {
            'sub': user_id,
            'role': role,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=self.token_expire_hours)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def verify_token(self, token: str) -> Dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception('Token has expired')
        except jwt.InvalidTokenError:
            raise Exception('Invalid token')
