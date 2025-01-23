
from flask import Blueprint, jsonify
from app.utils.analytics.user_analytics import UserAnalytics
from app.utils.auth import auth_required

bp = Blueprint('analytics', __name__)
analytics = UserAnalytics()

@bp.route('/api/v1/analytics/user/<int:user_id>', methods=['GET'])
@auth_required
async def get_user_analytics(user_id: int):
    metrics = await analytics.get_user_metrics(user_id)
    performance = await analytics.get_performance_metrics(user_id)
    
    return jsonify({
        'metrics': metrics,
        'performance': performance
    })
