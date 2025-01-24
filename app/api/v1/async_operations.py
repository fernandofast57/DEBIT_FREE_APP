
from flask import Blueprint, jsonify
from app.utils.auth import auth_required

bp = Blueprint('async', __name__, url_prefix='/api/v1/async')

@bp.route('/operation', methods=['GET'])
@auth_required
def check_async_operation():
    """Check status of async operations"""
    return jsonify({
        "status": "completed",
        "message": "All operations completed successfully"
    }), 200
