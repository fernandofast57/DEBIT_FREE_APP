
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
from functools import wraps
from flask import request, jsonify, current_app

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

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
            
        token = token.split(' ')[1] if ' ' in token else token
        auth_manager = AuthManager(current_app.config['SECRET_KEY'])
        payload = auth_manager.verify_token(token)
        
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
            
        request.user_id = payload.get('user_id')
        return f(*args, **kwargs)
    return decorated
