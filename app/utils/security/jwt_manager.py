
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional
from flask import current_app

class JWTManager:
    def __init__(self):
        self.secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        self.token_expire_hours = current_app.config.get('JWT_TOKEN_EXPIRE_HOURS', 24)

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
