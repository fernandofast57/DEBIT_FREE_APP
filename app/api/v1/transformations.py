from flask import Blueprint, jsonify, request
from app.services.transformation_service import TransformationService
from app.utils.auth import auth_required
from app.utils.security.rate_limiter import rate_limit
import asyncio

transformations_bp = Blueprint('transformations_bp', __name__)
transformation_service = TransformationService()

@transformations_bp.route('/transform', methods=['POST'])
@auth_required
@rate_limit(max_requests=5, window_size=60)
async def transform_gold():
    """
    Transform money into gold investment
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            euro_amount:
              type: number
              description: Amount in euros to transform
              example: 100.0
            fixing_price:
              type: number
              description: Current gold fixing price
              example: 50.0
    responses:
      200:
        description: Successful transformation
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            transaction_id:
              type: string
              example: "trans_123456"
      400:
        description: Invalid input
      401:
        description: Unauthorized
    tags:
      - Gold Transformations
    """
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