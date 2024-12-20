
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
        self.gold_reward_thresholds = {
            'bronze': Decimal('5000'),    # 0.1g gold
            'silver': Decimal('10000'),   # 0.25g gold
            'gold': Decimal('25000'),     # 0.5g gold
            'platinum': Decimal('50000')  # 1g gold
        }
        self.gold_reward_amounts = {
            'bronze': Decimal('0.1'),
            'silver': Decimal('0.25'),
            'gold': Decimal('0.5'),
            'platinum': Decimal('1.0')
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
        """Distribute bonus to exactly 3 levels up if possible, no more"""
        distribution_results = {}
        current_user = await User.query.get(buyer_id)
        level = 1
        

    async def calculate_gold_reward(self, user_id: int, transaction_amount: Decimal) -> Optional[Decimal]:
        """Calculate gold reward based on transaction amount"""
        user = await User.query.get(user_id)
        if not user:
            return None
            
        total_volume = user.total_investment + transaction_amount
        
        for level, threshold in sorted(self.gold_reward_thresholds.items(), 
                                    key=lambda x: x[1], reverse=True):
            if total_volume >= threshold:
                return self.gold_reward_amounts[level]
                
        return Decimal('0')
        
    async def distribute_gold_reward(self, user_id: int, transaction_amount: Decimal):
        """Distribute gold reward if threshold is met"""
        gold_amount = await self.calculate_gold_reward(user_id, transaction_amount)
        
        if gold_amount > 0:
            reward = GoldReward(
                user_id=user_id,
                gold_amount=gold_amount,
                reward_type='achievement'
            )
            db.session.add(reward)
            
            user = await User.query.get(user_id)
            user.gold_account.balance += gold_amount
            
            await db.session.commit()
            logger.info(f"Gold reward distributed to user {user_id}: {gold_amount}g")

        # Strict 3-level limit
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
