from flask import Blueprint, jsonify, request
from app.services.transformation_service import TransformationService
from app.schemas.transformation_schema import TransformationSchema
from marshmallow import ValidationError

transformations_bp = Blueprint('transformations', __name__)
performance_bp = Blueprint('performance', __name__) # New Blueprint for performance endpoint

transformation_service = TransformationService()

# Assuming performance_monitor is defined elsewhere
# Example:  performance_monitor = PerformanceMonitor()

@transformations_bp.route('/transform', methods=['POST'])
async def transform_gold():
    """Handles gold transformation requests."""
    if not request.headers.get('X-User-Id'):
        return jsonify({"error": "Authentication required"}), 401
        
    schema = TransformationSchema()
    try:
        data = schema.load(request.json)
        result = await transformation_service.transform_to_gold(
            user_id=request.headers.get('X-User-Id'),
            fixing_price=data['fixing_price'],
            euro_amount=data['euro_amount'],
            fee_amount=data['fee_amount'],
            gold_grams=data['gold_grams']
        )
        return jsonify(result), 200
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@performance_bp.route('/performance', methods=['GET']) # New endpoint
def get_performance_metrics():
    return jsonify({
        'transformation': performance_monitor.get_metrics('transformation'),
        'api_response': performance_monitor.get_metrics('api_response'),
        'database_query': performance_monitor.get_metrics('database_query')
    })