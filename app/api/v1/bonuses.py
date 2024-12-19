# app/api/v1/bonuses.py
from flask import Blueprint, jsonify, request
from decimal import Decimal
from app.services.bonus_distribution_service import BonusDistributionService

bp = Blueprint('bonuses', __name__, url_prefix='/api/v1/bonuses')
bonus_service = BonusDistributionService()

@bp.route('/distribute', methods=['POST'])
def distribute_bonus():
    """
    Distribuisce i bonus per una transazione
    {
        "user_id": 1,
        "transaction_amount": 1000.00
    }
    """
    data = request.get_json()

    try:
        user_id = int(data.get('user_id'))
        transaction_amount = Decimal(str(data.get('transaction_amount')))
    except (TypeError, ValueError):
        return jsonify({
            'status': 'error',
            'message': 'Parametri non validi'
        }), 400

    result = bonus_service.distribute_transaction_bonus(user_id, transaction_amount)

    if result['status'] == 'error':
        return jsonify(result), 400

    return jsonify(result)

@bp.route('/history/<int:user_id>', methods=['GET'])
def get_bonus_history(user_id):
    """Recupera lo storico bonus di un utente"""
    result = bonus_service.get_user_bonus_history(user_id)

    if result['status'] == 'error':
        return jsonify(result), 400

    return jsonify(result)
from flask import Blueprint, jsonify
from app.services.bonus_distribution_service import BonusDistributionService
from app.utils.auth import auth_required
from app.utils.security.rate_limiter import rate_limit

bp = Blueprint('bonuses', __name__)
bonus_service = BonusDistributionService()

@bp.route('/calculate', methods=['GET'])
@auth_required
@rate_limit(requests=5, window=60)
def calculate_bonus():
    """Calculate potential bonus for current user"""
    try:
        from flask import request
        user_id = request.user_id
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        bonus = bonus_service.calculate_user_bonus(user)
        return jsonify({
            'bonus_amount': float(bonus),
            'rank': user.noble_rank.rank_name if user.noble_rank else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/statistics', methods=['GET'])
@auth_required
@rate_limit(requests=5, window=60)
def bonus_statistics():
    """Get bonus distribution statistics"""
    try:
        stats = bonus_service.get_bonus_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
