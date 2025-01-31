from typing import Dict, Any, List
from datetime import datetime
import logging
from decimal import Decimal
from app.models import db
from app.models.models import Transaction, User, TransactionApproval
from app.services.notification_service import NotificationService
from app.services.kyc_service import KYCService

logger = logging.getLogger(__name__)

class WorkflowService:
    def __init__(self):
        self.notification_service = NotificationService()
        self.kyc_service = KYCService()

    async def start_approval_workflow(self, transaction_id: int) -> Dict[str, Any]:
        """Start the approval workflow for a new transaction"""
        try:
            transaction = await Transaction.query.get(transaction_id)
            if not transaction:
                raise ValueError("Transaction not found")

            workflow_data = {
                'status': 'initiated',
                'current_step': 'document_validation',
                'started_at': datetime.utcnow(),
                'steps_completed': [],
                'fixing_price': None,
                'spread_applied': Decimal('0.067')  # 6.7% as per requirements
            }

            transaction.workflow_data = workflow_data
            await db.session.commit()

            await self.notification_service.notify_operators(
                "New transaction requires validation",
                f"Transaction {transaction_id} workflow started"
            )

            return workflow_data

    async def process_step(self, transaction_id: int, step: str, action: str, notes: str = None) -> Dict[str, Any]:
        """Process a single workflow step"""
        try:
            transaction = await Transaction.query.get(transaction_id)
            if not transaction:
                raise ValueError("Transaction not found")

            if action not in ['approve', 'reject']:
                raise ValueError("Invalid action")

            workflow_data = transaction.workflow_data
            workflow_data['steps_completed'].append({
                'step': step,
                'action': action,
                'timestamp': datetime.utcnow().isoformat(),
                'notes': notes
            })

            if action == 'approve':
                next_steps = {
                    'document_validation': 'kyc_verification',
                    'kyc_verification': 'financial_check',
                    'financial_check': 'completed'
                }
                workflow_data['current_step'] = next_steps.get(step, 'completed')

                if step == 'financial_check':
                    workflow_data['status'] = 'ready_for_transformation'
            else:
                workflow_data['status'] = 'rejected'

            transaction.workflow_data = workflow_data
            await db.session.commit()

            return workflow_data

    async def process_weekly_transformation(self, transaction_id: int, fixing_price: Decimal) -> Dict[str, Any]:
        """Process weekly euro to gold transformation"""
        transaction = await Transaction.query.get(transaction_id)
        if not transaction:
            raise ValueError("Transaction not found")

        if transaction.workflow_data['status'] != 'ready_for_transformation':
            raise ValueError("Transaction not ready for transformation")

        workflow_data = transaction.workflow_data
        workflow_data['fixing_price'] = str(fixing_price)
        workflow_data['transformation_date'] = datetime.utcnow().isoformat()
        workflow_data['status'] = 'transformed'

        transaction.status = 'completed'
        await db.session.commit()

        await self.notification_service.notify_user(
            transaction.user_id,
            f"Your transaction has been transformed at fixing price {fixing_price}"
        )

        return workflow_data

    async def get_workflow_status(self, transaction_id: int) -> Dict[str, Any]:
        transaction = await Transaction.query.get(transaction_id)
        if not transaction:
            raise ValueError("Transaction not found")
        return transaction.workflow_data

    async def process_admin_approval(self, transaction_id: int, admin_id: int, action: str):
        """Process admin approval for a transaction"""
        transaction = await Transaction.query.get(transaction_id)
        if not transaction:
            raise ValueError("Transaction not found")

        if action not in ['approve', 'reject']:
            raise ValueError("Invalid action")

        approval = TransactionApproval(
            transaction_id=transaction_id,
            validator_id=admin_id,
            status=action,
            validation_result={
                'action': action,
                'timestamp': datetime.utcnow().isoformat(),
                'validator_id': admin_id
            }
        )

        transaction.status = 'approved' if action == 'approve' else 'rejected'
        db.session.add(approval)
        await db.session.commit()

        await self.notification_service.notify_user(
            transaction.user_id,
            f"Your transaction has been {action}d by an administrator"
        )

        return {
            'status': action,
            'processed_by': admin_id,
            'timestamp': datetime.utcnow().isoformat()
        }