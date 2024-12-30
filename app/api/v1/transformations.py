
from flask import Blueprint, jsonify, request
from app.services.transformation_service import TransformationService
from app.schemas.transformation_schema import TransformationSchema
from marshmallow import ValidationError
from decimal import Decimal

transformations_bp = Blueprint('transformations', __name__)
performance_bp = Blueprint('performance', __name__)

transformation_service = TransformationService()

@transformations_bp.route('/transform', methods=['POST'])
async def transform_gold():
    """Handles gold transformation requests."""
    user_id = request.headers.get('X-User-Id')
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401
    
    schema = TransformationSchema()
    try:
        data = schema.load(request.json)
        result = await transformation_service.transform_to_gold(
            user_id=int(request.headers.get('X-User-Id')),
            fixing_price=data['fixing_price'],
            gold_grams=data['gold_grams']
        )
        return jsonify(result), 200
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transformations_bp.route('/process-weekly', methods=['POST'])
async def process_weekly_transformations():
    """Process weekly transformations with current fixing price"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
            
        data = request.get_json()
        fixing_price = Decimal(str(data.get('fixing_price', 0)))
        
        if fixing_price <= 0:
            return jsonify({'error': 'Invalid fixing price'}), 400
            
        weekly_service = WeeklyProcessingService()
        result = await weekly_service.process_weekly_transformations(fixing_price)
        
        return jsonify(result), 200 if result['status'] == 'success' else 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@performance_bp.route('/performance', methods=['GET'])
def get_performance_metrics():
    return jsonify({
        'transformation': performance_monitor.get_metrics('transformation'),
        'api_response': performance_monitor.get_metrics('api_response'),
        'database_query': performance_monitor.get_metrics('database_query')
    })
from flask import Blueprint, request, jsonify
from app.services.transformation_service import TransformationService
from app.utils.auth import require_auth
from decimal import Decimal
import logging

transformations_bp = Blueprint('transformations', __name__)
logger = logging.getLogger(__name__)

@transformations_bp.route('/transform', methods=['POST'])
@require_auth
async def transform():
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
            fixing_price=fixing_price
        )
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Transform error: {str(e)}")
        return jsonify({'error': str(e)}), 500
