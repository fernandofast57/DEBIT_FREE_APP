from decimal import Decimal
import logging
from datetime import datetime
from typing import Optional, Dict

from app.models import db
from app.models.models import User, Transaction, GoldAccount, MoneyAccount
from app.utils.blockchain_service import BlockchainService
from app.utils.validation_report import ValidationReport

logger = logging.getLogger(__name__)

class TransformationService:
    def __init__(self):
        self.blockchain_service = BlockchainService()

    async def process_transformation(self, user_id: int, amount: Decimal) -> Dict:
        """Process a gold transformation with validation and blockchain recording"""
        try:
            # Validate transformation
            validation = self._validate_transformation(user_id, amount)
            if not validation.is_valid:
                return {"success": False, "error": validation.error_message}

            user = User.query.get(user_id)
            money_account = MoneyAccount.query.filter_by(user_id=user_id).first()
            gold_account = GoldAccount.query.filter_by(user_id=user_id).first()

            # Calculate gold amount with current fixing
            gold_amount = self._calculate_gold_amount(amount)

            # Begin transaction
            db.session.begin(nested=True)
            try:
                # Update accounts
                money_account.balance -= amount
                gold_account.balance += gold_amount

                # Create transaction record
                transaction = Transaction(
                    user_id=user_id,
                    type='TRANSFORM',
                    amount=amount,
                    gold_amount=gold_amount,
                    status='PENDING'
                )
                db.session.add(transaction)

                # Record on blockchain
                tx_hash = await self.blockchain_service.record_transformation(
                    user.blockchain_address,
                    float(amount),
                    float(gold_amount)
                )

                transaction.blockchain_tx = tx_hash
                transaction.status = 'COMPLETED'

                db.session.commit()
                logger.info(f"Transformation completed for user {user_id}")

                return {
                    "success": True,
                    "transaction_id": transaction.id,
                    "gold_amount": float(gold_amount),
                    "tx_hash": tx_hash
                }

            except Exception as e:
                db.session.rollback()
                logger.error(f"Transformation failed: {str(e)}")
                return {"success": False, "error": "Transaction failed"}

        except Exception as e:
            logger.error(f"Transformation processing error: {str(e)}")
            return {"success": False, "error": "Processing error"}

    def _validate_transformation(self, user_id: int, amount: Decimal) -> ValidationReport:
        """Validate transformation request"""
        validation = ValidationReport()

        money_account = MoneyAccount.query.filter_by(user_id=user_id).first()
        if not money_account:
            validation.add_error("Money account not found")
            return validation

        if amount <= 0:
            validation.add_error("Amount must be positive")
            return validation

        if money_account.balance < amount:
            validation.add_error("Insufficient funds")
            return validation

        return validation

    def _calculate_gold_amount(self, amount: Decimal) -> Decimal:
        """Calculate gold amount based on current fixing price"""
        # Implement actual fixing price logic here
        fixing_price = Decimal('1800.00')  # Example fixed price
        return amount / fixing_price * Decimal('0.95')  # Apply 5% spread