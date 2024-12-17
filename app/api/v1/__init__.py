
from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api.v1 import bonuses, transfers, transformations
from flask import Blueprint

bp = Blueprint('api_v1', __name__)

from app.api.v1 import transformations, transfers, bonuses
