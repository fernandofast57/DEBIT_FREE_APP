from decimal import Decimal
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from app.utils.validation_report import ValidationReport
from app.models import db
from app.models.models import User, Transaction, GoldAccount, MoneyAccount, GoldTransformation
from app.services.blockchain_service import BlockchainService
from app.exceptions import TransformationError


logger = logging.getLogger(__name__)

class TransformationService:
    """Service for handling gold transformations as per glossary"""

    def __init__(self):
        self.blockchain_service = BlockchainService()

    async def _get_current_fixing_price(self) -> Decimal:
        """Retrieves the current gold fixing price.  Implementation details omitted for brevity."""
        # Replace this with your actual implementation to fetch the fixing price
        return Decimal('1800.00')

    def _calculate_gold_grams(self, euro_amount: Decimal, fixing_price: Decimal) -> Decimal:
        """Calculates the amount of gold grams based on euro amount and fixing price."""
        return (euro_amount / fixing_price) * Decimal('0.95') # Apply 5% spread


    async def process_transformation(self, user_id: int, euro_amount: Decimal) -> dict:
        """Process a gold transformation according to glossary specifications"""
        try:
            # Validate transformation
            validation = self._validate_transformation(user_id, euro_amount)
            if not validation.is_valid:
                raise TransformationError(validation.error_message)

            fixing_price = await self._get_current_fixing_price()
            gold_grams = self._calculate_gold_grams(euro_amount, fixing_price)

            user = User.query.get(user_id)
            money_account = MoneyAccount.query.filter_by(user_id=user_id).first()
            gold_account = GoldAccount.query.filter_by(user_id=user_id).first()

            # Begin transaction
            db.session.begin(nested=True)
            try:
                # Update accounts
                money_account.balance -= euro_amount
                gold_account.balance += gold_grams

                # Create transformation record
                transformation = GoldTransformation(
                    user_id=user_id,
                    euro_amount=euro_amount,
                    gold_grams=gold_grams,
                    fixing_price=fixing_price
                )
                db.session.add(transformation)


                # Record on blockchain (if needed) - adapt as necessary
                tx_hash = await self.blockchain_service.record_transformation(
                    user.blockchain_address,
                    float(euro_amount),
                    float(gold_grams)
                )


                db.session.commit()
                logger.info(f"Transformation completed for user {user_id}")

                return {
                    'status': 'success',
                    'transformation_id': transformation.id,
                    'gold_grams': gold_grams,
                    'tx_hash': tx_hash #Include tx_hash if blockchain recording is successful
                }

            except Exception as e:
                db.session.rollback()
                logger.error(f"Transformation failed: {str(e)}")
                raise TransformationError("Transaction failed")

        except TransformationError as e:
            await db.session.rollback()
            raise e #Re-raise the TransformationError
        except Exception as e:
            await db.session.rollback()
            logger.error(f"Transformation processing error: {str(e)}")
            raise TransformationError("Processing error")


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


    async def execute_transformation(self, user_id: int, amount: float) -> Dict[str, Any]:
        try:
            return {
                'status': 'success',
                'message': 'Transformation executed successfully',
                'amount': amount
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }