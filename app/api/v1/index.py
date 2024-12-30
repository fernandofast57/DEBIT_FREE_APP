
from flask import Blueprint
from . import (
    accounting,
    async_operations,
    bonuses,
    noble,
    notifications,
    system,
    transfers,
    transformations,
    validation
)

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Register all routes
api_v1.register_blueprint(accounting.bp)
api_v1.register_blueprint(async_operations.bp)
api_v1.register_blueprint(bonuses.bp)
api_v1.register_blueprint(noble.bp)
api_v1.register_blueprint(notifications.bp)
api_v1.register_blueprint(system.bp)
api_v1.register_blueprint(transfers.bp)
api_v1.register_blueprint(transformations.bp)
api_v1.register_blueprint(validation.bp)
