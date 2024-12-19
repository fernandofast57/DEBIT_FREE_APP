from flask import Blueprint, jsonify, request
from decimal import Decimal, InvalidOperation
from app.services.transformation_service import TransformationService

bp = Blueprint('transformations', __name__, url_prefix='/api/v1/transformations')
transformation_service = TransformationService()

@bp.route('/transform', methods=['POST'])
async def validate_bank_transfer():
    """
    Validazione bonifico da parte del tecnico
    {
        "technician_id": 1,
        "transaction_id": 123
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({'status': 'error', 'message': 'Dati mancanti'}), 400

    technician_id = data.get('technician_id')
    transaction_id = data.get('transaction_id')

    if not technician_id or not transaction_id:
        return jsonify({'status': 'error', 'message': 'Parametri mancanti'}), 400

    result = transformation_service.validate_transfer(technician_id, transaction_id)
    return jsonify(result)

@bp.route('/tuesday-gold-purchase', methods=['POST'])
async def execute_gold_purchase():
    """
    Esegue acquisto oro del martedì e distribuisce ai clienti
    {
        "technician_id": 1,
        "fixing_price": 1850.50
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({'status': 'error', 'message': 'Dati mancanti'}), 400

    try:
        technician_id = int(data.get('technician_id'))
        fixing_price = Decimal(str(data.get('fixing_price')))
    except (TypeError, ValueError, InvalidOperation):
        return jsonify({'status': 'error', 'message': 'Parametri non validi'}), 400

    result = transformation_service.execute_tuesday_gold_purchase(technician_id, fixing_price)
    return jsonify(result)
    """
    Trasforma il saldo euro in oro
    {
        "user_id": 1,
        "fixing_price": 1800.50
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({
            'status': 'error',
            'message': 'Dati JSON mancanti'
        }), 400

    try:
        user_id = int(data.get('user_id'))
    except (TypeError, ValueError):
        return jsonify({
            'status': 'error',
            'message': 'User ID non valido'
        }), 400

    try:
        fixing_price = Decimal(str(data.get('fixing_price')))
        if fixing_price <= 0:
            raise ValueError("Fixing price deve essere maggiore di zero")
    except (InvalidOperation, ValueError, TypeError) as e:
        return jsonify({
            'status': 'error',
            'message': f'Fixing price non valido: {str(e)}'
        }), 400

    result = await transformation_service.transform_to_gold(user_id, fixing_price)

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