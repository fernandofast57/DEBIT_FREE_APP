
from decimal import Decimal
from typing import Dict, Optional
from datetime import datetime
from app.models.models import User, GoldReward
from app.utils.logging_config import logger
from app import db

class BonusDistributionService:
    def __init__(self):
        # Structure bonus rates (% of purchase converted to gold)
        self.bonus_rates = {
            'level_1': Decimal('0.007'),  # 0.7%
            'level_2': Decimal('0.005'),  # 0.5%
            'level_3': Decimal('0.005')   # 0.5%
        }
        
        # Achievement thresholds in euros
        self.achievement_thresholds = {
            'bronze': Decimal('5000'),    # 5,000€
            'silver': Decimal('10000'),   # 10,000€
            'gold': Decimal('25000'),     # 25,000€
            'platinum': Decimal('50000')  # 50,000€
        }
        
        # Achievement rewards in gold grams
        self.achievement_rewards = {
            'bronze': Decimal('0.1000'),    # 0.1g
            'silver': Decimal('0.2500'),    # 0.25g
            'gold': Decimal('0.5000'),      # 0.5g
            'platinum': Decimal('1.0000')   # 1.0g
        }

    async def distribute_rewards(self, user_id: int, euro_amount: Decimal, fixing_price: Decimal) -> Dict:
        """Distribute both structure and achievement rewards"""
        structure_rewards = await self.distribute_structure_bonus(user_id, euro_amount, fixing_price)
        achievement_reward = await self.distribute_achievement_reward(user_id, euro_amount, fixing_price)
        
        return {
            'structure_rewards': structure_rewards,
            'achievement_reward': achievement_reward
        }

    async def distribute_structure_bonus(self, user_id: int, euro_amount: Decimal, fixing_price: Decimal) -> Dict:
        """Distribute structure bonus in gold based on euro amount"""
        distribution_results = {}
        current_user = await User.query.get(user_id)
        level = 1
        
        while current_user.referrer_id and level <= 3:
            referrer = await User.query.get(current_user.referrer_id)
            if not referrer:
                break
                
            bonus_euro = euro_amount * self.bonus_rates[f'level_{level}']
            bonus_gold = (bonus_euro / fixing_price).quantize(Decimal('0.0001'))
            
            if bonus_gold > 0:
                reward = GoldReward(
                    user_id=referrer.id,
                    gold_amount=bonus_gold,
                    reward_type='structure',
                    level=level,
                    euro_amount=bonus_euro,
                    fixing_price=fixing_price,
                    threshold_reached=euro_amount
                )
                db.session.add(reward)
                
                referrer.gold_account.balance += bonus_gold
                distribution_results[referrer.id] = {
                    'level': level,
                    'gold_amount': float(bonus_gold)
                }
            
            current_user = referrer
            level += 1
        
        await db.session.commit()
        return distribution_results

    async def distribute_achievement_reward(self, user_id: int, euro_amount: Decimal, fixing_price: Decimal) -> Optional[Dict]:
        """Distribute achievement rewards based on investment thresholds"""
        user = await User.query.get(user_id)
        if not user:
            return None
            
        total_investment = user.total_investment + euro_amount
        
        for level, threshold in sorted(self.achievement_thresholds.items(), 
                                    key=lambda x: x[1], reverse=True):
            if total_investment >= threshold:
                gold_reward = self.achievement_rewards[level]
                
                reward = GoldReward(
                    user_id=user_id,
                    gold_amount=gold_reward,
                    reward_type='achievement',
                    threshold_reached=threshold,
                    euro_amount=euro_amount,
                    fixing_price=fixing_price
                )
                db.session.add(reward)
                
                user.gold_account.balance += gold_reward
                await db.session.commit()
                
                return {
                    'level': level,
                    'gold_amount': float(gold_reward),
                    'threshold': float(threshold)
                }
        
        return None
