
from decimal import Decimal
from typing import Dict, Any
from app.models.models import User, MoneyAccount, GoldAccount
from app.utils.performance_monitor import performance_monitor

class TransformationService:
    @performance_monitor.track_time('transformation')
    async def transform_to_gold(self, user_id: int, fixing_price: Decimal, gold_grams: Decimal) -> Dict[str, Any]:
        try:
            user = await User.query.get(user_id)
            if not user:
                raise ValueError("User not found")

            total_cost = fixing_price * gold_grams
            if user.money_account.balance < total_cost:
                raise ValueError("Insufficient funds")

            user.money_account.balance -= total_cost
            user.gold_account.balance += gold_grams

            return {
                "status": "success",
                "gold_grams": float(gold_grams),
                "cost": float(total_cost),
                "remaining_balance": float(user.money_account.balance)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
from decimal import Decimal
from typing import Dict, Any
from datetime import datetime
from app.models.models import User, MoneyAccount, GoldAccount, Transaction
from app.utils.blockchain_monitor import BlockchainMonitor
from app.database import db
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class TransformationService:
    FEE_PERCENTAGE = Decimal('0.05')  # 5% commissione

    @staticmethod
    async def process_transformation(user_id: int, euro_amount: Decimal, fixing_price: Decimal) -> Dict[str, Any]:
        try:
            user = User.query.get(user_id)
            if not user or not user.money_account or not user.gold_account:
                raise ValueError("User or accounts not found")

            # Calcolo secondo il test: (100 - 5% fee) / 50 = 1.90
            net_amount = euro_amount * (1 - TransformationService.FEE_PERCENTAGE)
            gold_grams = net_amount / fixing_price

            async with db.session.begin_nested():
                # Aggiorna i conti
                user.money_account.balance -= euro_amount
                user.gold_account.balance += gold_grams

                # Registra la transazione
                transaction = Transaction(
                    user_id=user_id,
                    type='transformation',
                    euro_amount=euro_amount,
                    gold_amount=gold_grams,
                    fee_amount=fee_amount,
                    fixing_price=fixing_price,
                    timestamp=datetime.utcnow()
                )
                db.session.add(transaction)
                await db.session.flush()

                # Registra sulla blockchain
                await BlockchainMonitor.record_transaction(transaction.id, euro_amount, gold_grams)

            await db.session.commit()
            return {
                "status": "success",
                "gold_grams": float(gold_grams),
                "transaction_id": transaction.id
            }

        except SQLAlchemyError as e:
            await db.session.rollback()
            logger.error(f"Database error during transformation: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error during transformation: {str(e)}")
            raise
