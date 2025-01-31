
from datetime import datetime, timedelta
import jwt
from flask import current_app
from typing import Optional, Dict

class JWTManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def generate_token(self, user_id: int, exp_days: int = 1) -> str:
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=exp_days)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def verify_token(self, token: str) -> Optional[Dict]:
        try:
            return jwt.decode(token, self.secret_key, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
