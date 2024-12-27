from flask import Blueprint, jsonify, request
from app.services.transformation_service import TransformationService
from app.utils.auth import auth_required
from app.utils.security.rate_limiter import rate_limit
import asyncio
from app.schemas.transformation_schema import TransformationSchema # Added import

transformations_bp = Blueprint('transformations_bp', __name__)
transformation_service = TransformationService()

@transformations_bp.route('/transform', methods=['POST'])
@auth_required
@rate_limit(max_requests=5, window_size=60)
async def transform_gold():
    try:
        schema = TransformationSchema()
        errors = schema.validate(request.get_json())
        if errors:
            return jsonify({"error": errors}), 400

        data = schema.load(request.get_json())
        result = await transformation_service.transform_to_gold(
            user_id=request.user_id,
            euro_amount=data['euro_amount']
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transformations_bp.route('/batch', methods=['POST'])
@auth_required
@rate_limit(max_requests=2, window_size=300)
async def batch_transform():
    try:
        data = request.get_json()
        transformations = data.get('transformations', [])
        if not transformations:
            return jsonify({'error': 'No transformations provided'}), 400

        result = await transformation_service.process_batch_transformations(transformations)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500