
from flask import Blueprint, jsonify, request
from app.services.transformation_service import TransformationService
from app.utils.auth import auth_required
from app.utils.security.rate_limiter import rate_limit
import asyncio

bp = Blueprint('transformations', __name__)
transformation_service = asyncio.run(TransformationService())

@bp.route('/transform', methods=['POST'])
@auth_required
@rate_limit(max_requests=5, window_size=60)
async def transform_gold():
    try:
        data = request.get_json()
        euro_amount = data.get('euro_amount')
        if not euro_amount:
            return jsonify({'error': 'Euro amount required'}), 400
            
        result = await transformation_service.transform_to_gold(
            user_id=request.user_id,
            euro_amount=euro_amount
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/batch', methods=['POST'])
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
