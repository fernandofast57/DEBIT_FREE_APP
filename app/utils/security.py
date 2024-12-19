
from flask import request
from functools import wraps
import re

def validate_address(address):
    """Validate Ethereum address format"""
    if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
        return False
    return True

def sanitize_input(data):
    """Sanitize user input"""
    if isinstance(data, str):
        return data.strip()
    return data

def require_valid_address(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        address = request.args.get('address', '')
        if not validate_address(address):
            return {'error': 'Invalid address format'}, 400
        return f(*args, **kwargs)
    return decorated
