from flask import Blueprint, jsonify, request
from app.services.bonus_distribution_service import BonusDistributionService
from app.utils.auth import auth_required
from app.utils.security.rate_limiter import rate_limit

bonuses_bp = Blueprint('bonuses_bp', __name__)
bonus_service = BonusDistributionService()

@bonuses_bp.route('/referral', methods=['GET'])
@auth_required
@rate_limit(max_requests=10, window_size=60)
def get_referral_bonuses():
    try:
        result = asyncio.run(bonus_service.get_referral_bonuses(request.user_id))
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bonuses_bp.route('/noble', methods=['GET'])
@auth_required
@rate_limit(max_requests=10, window_size=60)
def get_noble_bonuses():
    try:
        result = asyncio.run(bonus_service.get_noble_bonuses(request.user_id))
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bonuses_bp.route('/distribute', methods=['POST'])
@auth_required
@rate_limit(max_requests=2, window_size=300)
async def distribute_bonuses():
    try:
        data = request.get_json()
        transaction_id = data.get('transaction_id')
        if not transaction_id:
            return jsonify({'error': 'Transaction ID required'}), 400
            
        result = await bonus_service.distribute_bonuses(transaction_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500