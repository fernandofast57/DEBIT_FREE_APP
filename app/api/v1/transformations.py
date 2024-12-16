from flask import Blueprint, jsonify, request
from decimal import Decimal, InvalidOperation
from app.services.transformation_service import TransformationService

bp = Blueprint('transformations', __name__, url_prefix='/api/v1/transformations')
transformation_service = TransformationService()

@bp.route('/transform', methods=['POST'])
def transform_to_gold():
    """
    Trasforma il saldo euro in oro
    {
        "user_id": 1,
        "fixing_price": 1800.50
    }
    """
    data = request.get_json()

    try:
        user_id = int(data.get('user_id'))
        fixing_price = Decimal(str(data.get('fixing_price')))
    except (TypeError, ValueError, InvalidOperation):
        raise ValidationError('Parametri non validi')

    result = transformation_service.transform_to_gold(user_id, fixing_price)

    if result['status'] == 'error':
        return jsonify(result), 400

    return jsonify(result)

@bp.route('/weekly', methods=['POST'])
def process_weekly_transformations():
    """
    Processa tutte le trasformazioni settimanali
    {
        "fixing_price": 1800.50
    }
    """
    data = request.get_json()

    try:
        fixing_price = Decimal(str(data.get('fixing_price')))
    except (TypeError, ValueError, InvalidOperation):
        return jsonify({
            'status': 'error',
            'message': 'Fixing price non valido'
        }), 400

    result = transformation_service.process_weekly_transformations(fixing_price)

    if result['status'] == 'error':
        return jsonify(result), 400

    return jsonify(result)

@bp.route('/history/<int:user_id>', methods=['GET'])
def get_transformation_history(user_id):
    """Recupera lo storico delle trasformazioni di un utente"""
    result = transformation_service.get_transformation_history(user_id)

    if result['status'] == 'error':
        return jsonify(result), 400

    return jsonify(result)