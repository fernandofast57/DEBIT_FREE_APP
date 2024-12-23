
from flask import Blueprint, jsonify, request
from flask_httpauth import HTTPBasicAuth
from sqlalchemy.exc import SQLAlchemyError
from app import db
from werkzeug.exceptions import BadRequest

bp = Blueprint('api_v1', __name__)
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if username == 'admin' and password == 'password':
        return username
    return None

from .transformations import bp as transformations_bp
from .transfers import bp as transfers_bp
from .bonuses import bp as bonuses_bp
