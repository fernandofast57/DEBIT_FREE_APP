from flask import Blueprint, jsonify, request
from decimal import Decimal, InvalidOperation
from app.services.batch_collection_service import BatchCollectionService

bp = Blueprint('transfers', __name__, url_prefix='/api/v1/transfers')
transfer_service = BatchCollectionService()

@bp.route('/process', methods=['POST'])
def process_transfer():
    """
    Processa un singolo bonifico
    {
        "user_id": 1,
        "amount": 1000.00
    }
    """
    data = request.get_json()

    try:
        user_id = int(data.get('user_id'))
        amount = Decimal(str(data.get('amount')))
    except (TypeError, ValueError, InvalidOperation):
        return jsonify({
            'status': 'error',
            'message': 'Parametri non validi'
        }), 400

    result = transfer_service.process_bank_transfer(user_id, amount)

    if result['status'] == 'error':
        return jsonify(result), 400

    return jsonify(result)

@bp.route('/batch/add', methods=['POST'])
def add_to_batch():
    """
    Aggiunge un bonifico al batch settimanale
    {
        "user_id": 1,
        "amount": 1000.00
    }
    """
    data = request.get_json()

    try:
        user_id = int(data.get('user_id'))
        amount = Decimal(str(data.get('amount')))
    except (TypeError, ValueError, InvalidOperation):
        return jsonify({
            'status': 'error',
            'message': 'Parametri non validi'
        }), 400

    success = transfer_service.add_to_batch(user_id, amount)

    if not success:
        return jsonify({
            'status': 'error',
            'message': 'Errore nell\'aggiunta al batch'
        }), 400

    return jsonify({
        'status': 'success',
        'message': 'Bonifico aggiunto al batch'
    })

@bp.route('/batch/process', methods=['POST'])
def process_weekly_batch():
    """Processa tutti i bonifici in attesa nel batch"""
    result = transfer_service.process_weekly_batch()

    if result['status'] == 'error':
        return jsonify(result), 400

    return jsonify(result)

@bp.route('/batch/pending', methods=['GET'])
def get_pending_batch():
    """Recupera la lista dei bonifici in attesa"""
    pending = transfer_service.get_pending_batch()

    return jsonify({
        'status': 'success',
        'pending_transfers': pending
    })