import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from app.utils.security.security_manager import SecurityManager
from app.models.models import db

class AuthManager:
    def __init__(self):
        self.jwt_secret = os.environ.get('JWT_SECRET', 'default-secret')

    def generate_token(self, user_id: int, device_id: str) -> str:
        payload = {
            'user_id': user_id,
            'device_id': device_id,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')

    def verify_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return None

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Missing token'}), 401
            
        auth_manager = AuthManager() # Corrected instantiation
        payload = auth_manager.verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
            
        request.user_id = payload.get('user_id')
        return f(*args, **kwargs)
    return decorated