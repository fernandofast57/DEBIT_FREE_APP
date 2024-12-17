
from flask import Blueprint, jsonify, request
from app.models.models import User
from app.utils.auth import auth_required
from app import db

bp = Blueprint('affiliate', __name__)

@bp.route('/network', methods=['GET'])
@auth_required
def get_network():
    """Get user's affiliate network."""
    user_id = request.user_id
    
    # Get user's network
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    # Get direct affiliates
    affiliates = User.query.filter_by(referrer_id=user_id).all()
    
    network = [{
        'id': affiliate.id,
        'email': affiliate.email,
        'join_date': affiliate.created_at.isoformat(),
        'status': 'active'
    } for affiliate in affiliates]
    
    return jsonify({
        'network': network,
        'total_affiliates': len(network)
    })

@bp.route('/stats', methods=['GET'])
@auth_required
def get_stats():
    """Get affiliate statistics."""
    user_id = request.user_id
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    return jsonify({
        'total_earnings': 0.0,
        'active_affiliates': 0,
        'total_volume': 0.0
    })
