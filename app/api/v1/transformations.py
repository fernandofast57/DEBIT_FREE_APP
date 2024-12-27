
from flask import Blueprint, jsonify, request
from app.services.transformation_service import TransformationService
from app.schemas.transformation_schema import TransformationSchema
from marshmallow import ValidationError

transformations_bp = Blueprint('transformations_bp', __name__)
transformation_service = TransformationService()

@transformations_bp.route('/transform', methods=['POST'])
def transform_gold():
    """Handles gold transformation requests."""
    schema = TransformationSchema()
    try:
        data = schema.load(request.json)
        result = {
            "euro_amount": float(data['euro_amount']),
            "fixing_price": float(data['fixing_price']),
            "fee_amount": float(data['fee_amount']),
            "gold_grams": float(data['gold_grams'])
        }
        return jsonify({"message": "Gold transformed successfully", "data": result}), 200
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
