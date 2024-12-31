
from decimal import Decimal
from typing import Dict, Any, List
from datetime import datetime
from app.models.models import User, MoneyAccount, GoldAccount
from app.database import db
import logging

logger = logging.getLogger(__name__)

class TransformationService:
    ORGANIZATION_FEE = Decimal('0.05')  # 5% organization fee
    AFFILIATE_BONUS = {
        1: Decimal('0.007'),  # 0.7% first level
        2: Decimal('0.005'),  # 0.5% second level
        3: Decimal('0.005')   # 0.5% third level
    }

    @staticmethod
    async def verify_transfer(user_id: int, transfer_amount: Decimal) -> bool:
        """Verify if transfer is valid for transformation"""
        try:
            user = await User.query.get(user_id)
            return user and user.money_account.balance >= transfer_amount
        except Exception as e:
            logger.error(f"Transfer verification error: {str(e)}")
            return False

    @staticmethod
    async def process_organization_fee(amount: Decimal) -> Decimal:
        """Process 5% organization fee and return net amount"""
        fee_amount = amount * TransformationService.ORGANIZATION_FEE
        net_amount = amount - fee_amount
        # Here you would add logic to transfer fee to organization account
        return net_amount

    @staticmethod
    async def calculate_gold_amount(euro_amount: Decimal, fixing_price: Decimal) -> Decimal:
        """Calculate gold amount based on fixing price"""
        if fixing_price <= 0:
            raise ValueError("Invalid fixing price")
        return euro_amount / fixing_price

    @staticmethod
    async def distribute_affiliate_bonuses(user: User, gold_amount: Decimal):
        """Distribute affiliate bonuses up to 3 levels"""
        try:
            current_user = user
            for level in range(1, 4):
                if not current_user.referrer_id:
                    break
                    
                referrer = await User.query.get(current_user.referrer_id)
                if not referrer:
                    break
                    
                bonus_percentage = TransformationService.AFFILIATE_BONUS[level]
                bonus_amount = gold_amount * bonus_percentage
                
                if not referrer.gold_account:
                    continue
                    
                referrer.gold_account.balance += bonus_amount
                current_user = referrer
                
            await db.session.commit()
        except Exception as e:
            logger.error(f"Bonus distribution error: {str(e)}")
            await db.session.rollback()
            raise

    @staticmethod
    async def process_transformation(user_id: int, euro_amount: Decimal, fixing_price: Decimal) -> Dict[str, Any]:
        """Process complete money to gold transformation"""
        try:
            # 1. Verify transfer
            if not await TransformationService.verify_transfer(user_id, euro_amount):
                return {
                    "status": "error",
                    "message": "Invalid transfer or insufficient funds"
                }

            # 2. Process organization fee
            net_amount = await TransformationService.process_organization_fee(euro_amount)

            # 3. Calculate gold amount
            gold_amount = await TransformationService.calculate_gold_amount(net_amount, fixing_price)

            # 4. Process transformation
            async with db.session.begin():
                user = await User.query.get(user_id)
                
                # Update money and gold accounts
                user.money_account.balance -= euro_amount
                user.gold_account.balance += gold_amount
                user.gold_account.last_update = datetime.utcnow()

                # Distribute affiliate bonuses
                await TransformationService.distribute_affiliate_bonuses(user, gold_amount)
                
                await db.session.commit()

            return {
                "status": "success",
                "gold_grams": float(gold_amount),
                "transaction_id": None  # You can add transaction ID logic if needed
            }

        except Exception as e:
            logger.error(f"Transformation error: {str(e)}")
            await db.session.rollback()
            return {
                "status": "error",
                "message": str(e)
            }
