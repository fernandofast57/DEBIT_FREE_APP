
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
