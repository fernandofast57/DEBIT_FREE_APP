
from decimal import Decimal
from typing import Dict
import os
from app import db
from app.models.models import User
from app.utils.logging_config import logger

class BonusDistributionService:
    def __init__(self):
        self.bonus_rates = {
            'level_1': Decimal('0.007'),  # 0.7%
            'level_2': Decimal('0.005'),  # 0.5%
            'level_3': Decimal('0.005')   # 0.5%
        }
    
    def calculate_affiliate_bonus(self, purchase_amount: Decimal, level: int) -> Decimal:
        """Calculate bonus based on level and purchase amount"""
        if level == 1:
            return purchase_amount * self.bonus_rates['level_1']
        elif level == 2:
            return purchase_amount * self.bonus_rates['level_2']
        elif level == 3:
            return purchase_amount * self.bonus_rates['level_3']
        return Decimal('0')
    
    async def distribute_affiliate_bonus(self, buyer_id: int, purchase_amount: Decimal) -> Dict:
        """Distribute bonus to affiliates up to 3 levels up"""
        distribution_results = {}
        current_user = await User.query.get(buyer_id)
        level = 1
        
        while current_user.referrer_id and level <= 3:
            referrer = await User.query.get(current_user.referrer_id)
            if not referrer:
                break
                
            bonus = self.calculate_affiliate_bonus(purchase_amount, level)
            if bonus > 0:
                referrer.gold_account.balance += bonus
                distribution_results[referrer.id] = {
                    'level': level,
                    'bonus': float(bonus)
                }
                logger.info(f"Bonus distributed to user {referrer.id}: {bonus} at level {level}")
            
            current_user = referrer
            level += 1
        
        await db.session.commit()
        return distribution_results
