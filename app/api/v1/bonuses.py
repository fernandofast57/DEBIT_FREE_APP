from flask import Blueprint, jsonify, request
from app.services.bonus_distribution_service import BonusDistributionService
from app.utils.security.robust_rate_limiter import rate_limit
from app.utils.logging_config import get_logger

logger = get_logger(__name__)
bonuses_bp = Blueprint('bonuses', __name__)
# bonus_service = BonusDistributionService()


@bonuses_bp.route('/distribute', methods=['POST'])
async def distribute_bonuses():
    """Distribute bonuses to users"""
    bonus_service = BonusDistributionService()  # <-- LINEA AGGIUNTA QUI
    try:
        if not rate_limit.is_allowed(request.remote_addr):
            return jsonify({'error': 'Rate limit exceeded'}), 429

        transaction_id = request.json.get('transaction_id')
        if not transaction_id:
            return jsonify({'error': 'Transaction ID required'}), 400

        result = await bonus_service.distribute_bonuses(transaction_id)
        if result and 'status' in result:
            if result['status'] == 'success':
                return jsonify({
                    'status': 'success',
                    'message': 'Bonuses distributed successfully',
                    'details': result.get('details', {})
                }), 200

        return jsonify({
            'status': 'error',
            'message': 'Failed to distribute bonuses',
            'error': result.get('error', 'Unknown error')
        }), 500

    except Exception as e:
        logger.error(f"Error in bonus distribution: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bonuses_bp.route('/calculate', methods=['POST'])
async def calculate_bonuses():
    """Calculate bonuses for a transaction"""
    bonus_service = BonusDistributionService()  # <-- LINEA AGGIUNTA QUI
    try:
        if not rate_limit.is_allowed(request.remote_addr):
            return jsonify({'error': 'Rate limit exceeded'}), 429

        data = request.json
        user_id = data.get('user_id')
        amount = data.get('amount')

        if not user_id or not amount:
            return jsonify({'error': 'Missing required parameters'}), 400

        bonuses = await bonus_service.calculate_purchase_bonuses(
            user_id, amount)
        return jsonify({'bonuses': bonuses}), 200

    except Exception as e:
        logger.error(f"Error calculating bonuses: {str(e)}")
        return jsonify({'error': str(e)}), 500
