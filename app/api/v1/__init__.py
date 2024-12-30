from flask import Blueprint
from .async_operations import async_bp
from .accounting import bp as account_bp

from flask_httpauth import HTTPBasicAuth

# Main blueprint for API v1
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
api_v1.register_blueprint(async_bp, url_prefix='/async')
api_v1.register_blueprint(account_bp, url_prefix='/account')

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if username == 'admin' and password == 'password':  
        return username
    return None