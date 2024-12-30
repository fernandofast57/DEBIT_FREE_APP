
from flask import Blueprint, jsonify

bp = Blueprint('system', __name__)

@bp.route('/status', methods=['GET'])
async def get_status():
    """Async status check endpoint"""
    return jsonify({"status": "operational"}), 200
from flask import Blueprint, jsonify
from app.utils.performance_monitor import performance_monitor

system_bp = Blueprint('system', __name__)

@system_bp.route('/metrics', methods=['GET'])
async def get_system_metrics():
    """Get system performance metrics"""
    try:
        metrics = performance_monitor.get_metrics()
        return jsonify({
            'status': 'success',
            'metrics': metrics
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
