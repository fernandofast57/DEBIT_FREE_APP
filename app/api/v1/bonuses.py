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