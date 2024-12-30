
from decimal import Decimal
from typing import Dict, Any
from app.models.models import User
from app.database import db
import logging

logger = logging.getLogger(__name__)

class TransformationService:
    FEE_PERCENTAGE = Decimal('0.05')  # 5% fee

    @staticmethod
    async def process_transformation(user_id: int, euro_amount: Decimal, fixing_price: Decimal) -> Dict[str, Any]:
        try:
            user = await User.query.get(user_id)
            if not user or not user.money_account or not user.gold_account:
                raise ValueError("User or accounts not found")

            net_amount = euro_amount * (1 - TransformationService.FEE_PERCENTAGE)
            gold_grams = net_amount / fixing_price

            return {
                "status": "success",
                "gold_grams": float(gold_grams),
                "transaction_id": None
            }

        except Exception as e:
            logger.error(f"Error during transformation: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
