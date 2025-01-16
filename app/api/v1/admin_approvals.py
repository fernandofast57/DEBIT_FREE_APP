from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Transaction, TransactionApproval, UserActionLog # Added UserActionLog model
from app.database import db
from app.utils.blockchain_monitor import BlockchainMonitor
from decimal import Decimal
from sqlalchemy import exc

bp = Blueprint('admin_approvals', __name__, url_prefix='/api/v1/admin/approvals')
blockchain_monitor = BlockchainMonitor()

# Added UserActionLog model (assuming a suitable structure)
class UserActionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'))
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    details = db.Column(db.JSON)


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

        # Log the approval action
        action_log = UserActionLog(
            user_id=current_user.id,
            action='Transaction Approved',
            transaction_id=tx.id,
            details={'validation_result': validation_result}
        )
        db.session.add(action_log)


        db.session.commit()

        # Invia alla blockchain
        blockchain_result = blockchain_monitor.submit_to_blockchain(tx)

        return jsonify({
            'status': 'success',
            'blockchain_hash': blockchain_result['hash']
        })

    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error: Transaction already approved'}), 409 #Handle IntegrityError
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500