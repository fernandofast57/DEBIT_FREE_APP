
from functools import wraps
from flask import request, jsonify
from app.utils.security.security_manager import SecurityManager
from app.models.models import db

class AuthManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.security = SecurityManager(app_name="gold-investment")

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Missing token'}), 401
            
        auth_manager = AuthManager(secret_key="your-secret-key")
        payload = auth_manager.verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
            
        request.user_id = payload.get('user_id')
        return f(*args, **kwargs)
    return decorated
