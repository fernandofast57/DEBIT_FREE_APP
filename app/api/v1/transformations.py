
from flask import Blueprint, jsonify, request
from app.services.transformation_service import TransformationService
from app.utils.auth import auth_required
from app.utils.security.rate_limiter import rate_limit
from app.schemas.transformation_schema import TransformationSchema
from marshmallow import ValidationError

transformations_bp = Blueprint('transformations_bp', __name__)
transformation_service = TransformationService()

@transformations_bp.route('/transform', methods=['POST'])
@auth_required
@rate_limit(max_requests=5, window_size=60)
async def transform_gold():
    """Handles gold transformation requests."""
    schema = TransformationSchema()
    try:
        data = schema.load(request.json)
        result = await transformation_service.transform_to_gold(
            user_id=request.user_id,
            euro_amount=data['euro_amount']
        )
        return jsonify({"message": "Gold transformed successfully", "data": result}), 200
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
