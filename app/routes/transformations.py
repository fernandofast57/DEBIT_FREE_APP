
from flask import Blueprint, request, jsonify, g
from app.middleware.security import security
from app.services.transformation_service import TransformationService
from app.schemas.transformation_schema import TransformationSchema
from marshmallow import ValidationError

transform_bp = Blueprint('transformations', __name__)
transformation_service = TransformationService()

@transform_bp.route('/transform', methods=['POST'])
@security.require_auth
@security.rate_limit('transform')
async def transform():
    try:
        schema = TransformationSchema()
        data = schema.load(request.get_json())
        
        result = await transformation_service.execute_transformation(
            user_id=g.user_id,
            amount=data['amount'],
            currency=data['currency']
        )
        
        return jsonify({
            'status': 'success',
            'transaction_id': result['transaction_id'],
            'amount_transformed': result['amount']
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Transformation error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@transform_bp.route('/transform/status/<transaction_id>')
@security.require_auth
@security.rate_limit('api')
async def transform_status(transaction_id):
    try:
        status = await transformation_service.get_transformation_status(
            user_id=g.user_id,
            transaction_id=transaction_id
        )
        return jsonify(status), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
