
from flask import Blueprint, jsonify, request
from app.services.transformation_service import TransformationService
from app.schemas.transformation_schema import TransformationSchema
from marshmallow import ValidationError

transformations_bp = Blueprint('transformations', __name__)
transformation_service = TransformationService()

@transformations_bp.route('/transform', methods=['POST'])
async def transform_gold():
    """Handles gold transformation requests."""
    schema = TransformationSchema()
    try:
        data = schema.load(request.json)
        result = await transformation_service.transform_to_gold(
            user_id=request.headers.get('X-User-Id'),
            fixing_price=data['fixing_price']
        )
        return jsonify(result), 200
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
