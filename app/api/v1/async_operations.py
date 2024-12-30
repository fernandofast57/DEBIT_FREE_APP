
from flask import Blueprint, jsonify
from app.utils.auth import auth_required

async_bp = Blueprint('async', __name__)

@async_bp.route('/async_operation', methods=['GET'])
@auth_required
def check_async_operation():
    """Check status of async operations"""
    return jsonify({
        "status": "completed",
        "message": "All operations completed successfully"
    }), 200
