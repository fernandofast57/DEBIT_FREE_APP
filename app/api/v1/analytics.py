
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
from flask import Blueprint, jsonify
from app.services.analytics_service import AnalyticsService
from app.middleware.security import require_auth

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/metrics', methods=['GET'])
@require_auth
@validate_glossary_terms()
async def get_metrics():
    """Endpoint per metriche di sistema"""
    analytics = AnalyticsService(db.session)
    metrics = await analytics.get_system_metrics()
    return jsonify(metrics)

@analytics_bp.route('/noble-distribution', methods=['GET'])
@require_auth
async def get_noble_distribution():
    """Endpoint per distribuzione ranghi"""
    analytics = AnalyticsService(db.session)
    distribution = await analytics.get_noble_distribution()
    return jsonify(distribution)

@analytics_bp.route('/transaction-trends', methods=['GET'])
@require_auth
async def get_transaction_trends():
    """Endpoint per trend transazioni"""
    analytics = AnalyticsService(db.session)
    trends = await analytics.get_transaction_trends()
    return jsonify(trends)
