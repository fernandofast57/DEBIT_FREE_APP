
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Transaction, TransactionApproval
from app.database import db
from app.utils.blockchain_monitor import BlockchainMonitor
from decimal import Decimal

bp = Blueprint('admin_approvals', __name__, url_prefix='/api/v1/admin/approvals')
blockchain_monitor = BlockchainMonitor()

@bp.route('/pending', methods=['GET'])
@login_required
def get_pending_transactions():
    """Recupera le transazioni in attesa di approvazione"""
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    pending = Transaction.query.filter_by(status='pending_approval').all()
    return jsonify({
        'transactions': [{
            'id': tx.id,
            'user_id': tx.user_id,
            'amount': str(tx.amount),
            'type': tx.type,
            'validation_checks': blockchain_monitor.pre_validate_transaction(tx),
            'timestamp': tx.created_at.isoformat()
        } for tx in pending]
    })

@bp.route('/approve/<int:tx_id>', methods=['POST'])
@login_required
def approve_transaction(tx_id):
    """Approva una transazione dopo i controlli"""
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    tx = Transaction.query.get_or_404(tx_id)
    validation_result = blockchain_monitor.validate_transaction(tx)
    
    if not validation_result['valid']:
        return jsonify({
            'error': 'Validation failed',
            'details': validation_result['errors']
        }), 400

    try:
        # Registra l'approvazione
        approval = TransactionApproval(
            transaction_id=tx.id,
            admin_id=current_user.id,
            validation_report=validation_result
        )
        
        tx.status = 'approved'
        db.session.add(approval)
        db.session.commit()

        # Invia alla blockchain
        blockchain_result = blockchain_monitor.submit_to_blockchain(tx)
        
        return jsonify({
            'status': 'success',
            'blockchain_hash': blockchain_result['hash']
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
