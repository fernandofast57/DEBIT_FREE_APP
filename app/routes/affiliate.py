from flask import Blueprint, jsonify, request
from app.models.models import User
from app.utils.auth import auth_required
from app import db

affiliate_bp = Blueprint('affiliate_bp', __name__, url_prefix='/affiliate') # Added Blueprint definition

@affiliate_bp.route('/network', methods=['GET'])
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

@affiliate_bp.route('/stats', methods=['GET'])
@auth_required
def get_stats():
    """Get affiliate statistics."""
    user_id = request.user_id
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Get direct affiliates
    affiliates = User.query.filter_by(referrer_id=user_id).all()
    
    # Calculate stats
    total_volume = sum(affiliate.money_account.total_invested for affiliate in affiliates if affiliate.money_account)
    active_affiliates = sum(1 for affiliate in affiliates if affiliate.money_account and affiliate.money_account.total_invested > 0)
    total_earnings = sum(affiliate.money_account.referral_bonus for affiliate in affiliates if affiliate.money_account)
        
    return jsonify({
        'total_earnings': float(total_earnings),
        'active_affiliates': active_affiliates,
        'total_volume': float(total_volume)
    })