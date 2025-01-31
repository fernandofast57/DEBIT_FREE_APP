
from flask import Blueprint
from app.middleware.glossary_validator_middleware import validate_glossary_terms
from .transformations import transformations_bp
from .async_operations import bp as async_bp
from .accounting import bp as account_bp

# Main blueprint for API v1
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Register all blueprints
api_v1.register_blueprint(transformations_bp)
api_v1.register_blueprint(async_bp, url_prefix='/async')
api_v1.register_blueprint(account_bp, url_prefix='/account')
