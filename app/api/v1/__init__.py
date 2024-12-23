
from flask import Blueprint
from flask_httpauth import HTTPBasicAuth

# Main blueprint for API v1
bp = Blueprint('api_v1', __name__)
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if username == 'admin' and password == 'password':  
        return username
    return None
