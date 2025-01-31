
from typing import Dict, Optional
import jwt
import time
from datetime import datetime, timedelta
from flask import current_app

class SecurityManager:
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or current_app.config.get('SECRET_KEY')
        self._active_tokens: Dict[str, float] = {}
        self._session_monitor = {}

    def generate_token(self, user_id: int, role: str = 'user') -> str:
        payload = {
            'sub': user_id,
            'role': role,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        self._active_tokens[token] = time.time()
        return token

    def verify_token(self, token: str) -> dict:
        try:
            if token not in self._active_tokens:
                raise jwt.InvalidTokenError("Token not in active sessions")
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            self._active_tokens.pop(token, None)
            raise
        except jwt.InvalidTokenError:
            raise

    def revoke_token(self, token: str) -> bool:
        return bool(self._active_tokens.pop(token, None))
