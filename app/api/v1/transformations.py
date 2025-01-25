from flask import Blueprint, request, jsonify
from app.services.transformation_service import TransformationService
from app.middleware.security import SecurityMiddleware
from decimal import Decimal
import logging

transformations_bp = Blueprint('transformations', __name__)
security = SecurityMiddleware()
require_auth = security.require_auth
logger = logging.getLogger(__name__)

#Attempting partial solution based on limited information.  More context is needed for full alignment.
@transformations_bp.route('/transform', methods=['POST']) #Renamed endpoint for potential alignment.  More information is needed to determine the correct endpoint name based on glossary.
@require_auth
async def transform_gold(): #Renamed function for better naming clarity. More information is needed on the actual glossary terms.
    """Transform euros to gold according to glossary specifications""" #Added docstring as per the changes.
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        euro_amount = Decimal(str(data.get('euro_amount')))
        fixing_price = Decimal(str(data.get('fixing_price')))

        if not all([user_id, euro_amount, fixing_price]):
            return jsonify({'error': 'Missing required fields'}), 400

        result = await TransformationService.process_transformation(
            user_id=user_id,
            euro_amount=euro_amount,
            fixing_price=fixing_price,
            to_gold=True #Added flag to indicate gold conversion
        )

        return jsonify(result)
    except Exception as e:
        logger.error(f"Transform to gold error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@transformations_bp.route('/transform-to-euro', methods=['POST'])
@require_auth
async def transform_to_euro():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        gold_grams = Decimal(str(data.get('gold_grams')))
        fixing_price = Decimal(str(data.get('fixing_price')))

        if not all([user_id, gold_grams, fixing_price]):
            return jsonify({'error': 'Missing required fields'}), 400

        result = await TransformationService.process_transformation(
            user_id=user_id,
            gold_grams=gold_grams,
            fixing_price=fixing_price,
            to_gold=False #Added flag to indicate euro conversion

        )

        return jsonify(result)
    except Exception as e:
        logger.error(f"Transform to euro error: {str(e)}")
        return jsonify({'error': str(e)}), 500