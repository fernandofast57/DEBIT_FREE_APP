
from functools import wraps
from flask import request, jsonify
from flask_login import LoginManager, current_user
from app.models.models import User

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
            
        try:
            # Simple token validation for now
            token = auth_header.split(' ')[1]
            # Set a mock user_id for development
            request.user_id = 1
            return f(*args, **kwargs)
        except Exception:
            return jsonify({'error': 'Invalid token'}), 401
            
    return decorated
