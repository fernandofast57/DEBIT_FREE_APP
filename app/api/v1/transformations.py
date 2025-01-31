from flask import Blueprint, request, jsonify
from app.services.transformation_service import TransformationService
from app.middleware.security import SecurityMiddleware
from decimal import Decimal
import logging
from app.middleware.rate_limit import rate_limit
from app.middleware.audit_log import audit_log
from app.middleware.glossary_validator_middleware import validate_glossary_terms

transformations_bp = Blueprint('transformations', __name__)
security = SecurityMiddleware()
require_auth = security.require_auth
logger = logging.getLogger(__name__)

#Renamed endpoint and function for better clarity aligning with the requested terminology change.
@transformations_bp.route('/oro/trasforma', methods=['POST']) #Renamed endpoint
@require_auth
@validate_glossary_terms() #Added decorator
@rate_limit('api')  # As per OFFICIAL_STANDARDS.json rate limits
@audit_log(event_type='trasformazione_oro')  # As per USAGE.md
async def trasforma_in_oro(): #Renamed function
    """Trasforma denaro in oro fisico""" #Updated docstring
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
        logger.error(f"Trasformazione in oro error: {str(e)}") #Updated log message
        return jsonify({'error': str(e)}), 500

@transformations_bp.route('/oro/da_euro', methods=['POST']) #Renamed endpoint
@require_auth
@validate_glossary_terms() #Added decorator
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
        logger.error(f"Trasformazione da oro a euro error: {str(e)}") #Updated log message
        return jsonify({'error': str(e)}), 500