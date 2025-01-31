from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.services.workflow_service import WorkflowService
from app.models import Transaction, TransactionApproval, UserActionLog # Retained from original
from app.database import db
from app.utils.blockchain_monitor import BlockchainMonitor # Retained from original
from decimal import Decimal # Retained from original
from sqlalchemy import exc # Retained from original

bp = Blueprint('admin_approvals', __name__, url_prefix='/api/v1/admin/approvals')
workflow_service = WorkflowService()
blockchain_monitor = BlockchainMonitor() # Retained from original

# Added UserActionLog model (assuming a suitable structure) - Retained from original
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

    pending = Transaction.query.filter_by(status='pending_validation').all() #changed status
    return jsonify({
        'transactions': [{
            'id': tx.id,
            'user_id': tx.user_id,
            'amount': str(tx.amount),
            'type': tx.type,
            'timestamp': tx.created_at.isoformat()
        } for tx in pending]
    })


@bp.route('/validate/<int:tx_id>', methods=['POST'])
@login_required
def validate_transaction(tx_id):
    """Esegue la procedura guidata di validazione"""
    if not current_user.has_role(['admin', 'operator']):
        return jsonify({'error': 'Unauthorized'}), 403

    transaction = Transaction.query.get_or_404(tx_id)
    workflow_validator = WorkflowValidator() # Assuming this class exists elsewhere
    validation_result = workflow_validator.validate_transformation_workflow(transaction.to_dict())
    
    # Log dei passaggi di validazione
    audit_logger.log_action( # Assuming audit_logger is defined elsewhere
        'VALIDATION_WORKFLOW',
        current_user.id,
        f"Validation workflow completed for transaction {tx_id}",
        extra={
            'transaction_id': tx_id,
            'validation_result': validation_result
        }
    )

    # Salva il risultato della validazione
    approval = TransactionApproval(
        transaction_id=transaction.id,
        validator_id=current_user.id,
        validation_result=validation_result,
        status=validation_result['status']
    )

    db.session.add(approval)
    try:
        db.session.commit()
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error: Transaction already validated'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    # Log the validation action
    action_log = UserActionLog(
        user_id=current_user.id,
        action='Transaction Validated',
        transaction_id=transaction.id,
        details={'validation_result': validation_result}
    )
    db.session.add(action_log)
    db.session.commit()

    return jsonify(validation_result)


@bp.route('/certify/<int:tx_id>', methods=['POST'])
@login_required
def certify_transaction(tx_id):
    """Certifica la validità finale della transazione"""
    if not current_user.has_role('admin'):
        return jsonify({'error': 'Only administrators can certify transactions'}), 403

    approval = TransactionApproval.query.filter_by(
        transaction_id=tx_id,
        status='ready_for_certification'
    ).first_or_404()

    certification = validator.certify_transaction(
        approval.validation_result,
        current_user.id
    )

    if 'error' in certification:
        return jsonify(certification), 400

    approval.validation_result = certification
    approval.status = 'certified'
    tx = Transaction.query.get(tx_id)
    tx.status = 'approved'
    try:
        db.session.commit()
        blockchain_result = blockchain_monitor.submit_to_blockchain(tx)
        return jsonify({
            'status': 'success',
            'blockchain_hash': blockchain_result['hash']
        })
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error: Transaction already certified'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/workflow/<int:tx_id>/step/<step>', methods=['POST'])
@login_required
async def process_workflow_step(tx_id: int, step: str):
    if not current_user.has_role(['admin', 'operator']):
        return jsonify({'error': 'Unauthorized'}), 403

    action = request.json.get('action')
    try:
        result = await workflow_service.process_step(tx_id, step, action)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/workflow/<int:tx_id>', methods=['GET'])
@login_required
async def get_workflow_status(tx_id: int):
    try:
        result = await workflow_service.get_workflow_status(tx_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400