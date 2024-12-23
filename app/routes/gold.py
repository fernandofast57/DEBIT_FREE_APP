from flask import Blueprint, jsonify, request, current_app
from app.models.models import User, GoldAccount
from app.utils.auth import auth_required
from decimal import Decimal

bp = Blueprint('gold', __name__)

@bp.route('/balance', methods=['GET'])
@auth_required
def get_balance():
    """Get user's gold balance."""
    user_id = request.user_id
    
    # Get user's gold account
    user = User.query.get(user_id)
    if not user or not user.gold_account:
        return jsonify({'error': 'Gold account not found'}), 404
        
    return jsonify({
        'balance': float(user.gold_account.balance),
        'last_update': user.gold_account.last_update.isoformat()
    })

@bp.route('/transactions', methods=['GET'])
@auth_required
def get_transactions():
    """Get user's gold transactions history."""
    user_id = request.user_id
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    transformations = user.gold_transformations
    return jsonify({
        'transactions': [t.to_dict() for t in transformations]
    })