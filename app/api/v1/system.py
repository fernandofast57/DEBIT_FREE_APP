
from flask import Blueprint, jsonify

bp = Blueprint('system', __name__)

@bp.route('/status', methods=['GET'])
async def get_status():
    """Async status check endpoint"""
    return jsonify({"status": "operational"}), 200
