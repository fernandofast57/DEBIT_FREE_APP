from flask import Blueprint, jsonify, request
from decimal import Decimal, InvalidOperation
from app.services.batch_collection_service import BatchCollectionService
from app.middleware.transaction_validator_middleware import validate_transaction_flow

bp = Blueprint('transfers', __name__, url_prefix='/api/v1/transfers')
transfer_service = BatchCollectionService()

@bp.route('/process', methods=['POST'])
@validate_transaction_flow()
async def process_transfer():
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

@bp.route('/batch/process', methods=['POST'])
async def process_batch():
    """
    Processa un batch di bonifici
    {
        "transfers": [
            {
                "user_id": 1,
                "amount": 1000.00,
                "reference": "TRANSFER-001"
            },
            ...
        ]
    }
    """
    data = request.get_json()
    transfers = data.get('transfers', [])

    if not transfers:
        return jsonify({
            'status': 'error',
            'message': 'Nessun bonifico da processare'
        }), 400

    result = await transfer_service.process_batch_transfers(transfers)
    
    if result['status'] == 'error':
        return jsonify(result), 400

    return jsonify(result)
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

@bp.route('/fixing/purchase', methods=['POST'])
async def process_fixing_purchase():
    """Processa l'acquisto dell'oro al fixing"""
    data = request.get_json()
    
    try:
        technician_id = int(data.get('technician_id'))
        fixing_price = Decimal(str(data.get('fixing_price')))
    except (TypeError, ValueError, InvalidOperation):
        return jsonify({
            'status': 'error',
            'message': 'Parametri non validi'
        }), 400

    result = await transformation_service.process_fixing_purchase(technician_id, fixing_price)
    
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