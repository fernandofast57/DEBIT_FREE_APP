import os
from decimal import Decimal
from typing import Dict, Optional
from datetime import datetime
from app.models.models import User, GoldReward
from app.utils.logging_config import logger
from app import db

class BonusDistributionService:
    def __init__(self):
        self.blockchain_service = BlockchainService()
        
        self.bonus_rates = {
            'level_1': Decimal('0.007'),  # 0.7%
            'level_2': Decimal('0.005'),  # 0.5%
            'level_3': Decimal('0.005'),  # 0.5%
            'operational': Decimal('0.05') # 5.0%
            # Total network bonus: 1.7%
        }
        self.operational_wallet = os.getenv('OPERATIONAL_WALLET_ADDRESS')
        
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
        
        #Operational Fee Calculation and Distribution
        operational_fee_euro = euro_amount * self.bonus_rates['operational']
        operational_fee_gold = (operational_fee_euro / fixing_price).quantize(Decimal('0.0001'))

        if operational_fee_gold > 0 and self.operational_wallet:
            operational_reward = GoldReward(
                user_id=None, # Or assign to a specific operational wallet user if needed.
                gold_amount=operational_fee_gold,
                reward_type='operational',
                euro_amount=operational_fee_euro,
                fixing_price=fixing_price,
                threshold_reached=euro_amount
            )
            db.session.add(operational_reward)
            #In a real scenario, you'd likely interact with a separate wallet system here to transfer the gold.  This is placeholder logic.
            logger.info(f"Operational fee of {operational_fee_gold}g distributed to {self.operational_wallet}")

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
        
    async def calculate_bonus(self, user_id: int, transaction_amount: Decimal) -> Decimal:
        user = await User.query.get(user_id)
        if not user or not user.noble_rank:
            return Decimal('0')
            
        bonus_rate = await self._get_bonus_rate(user.noble_rank.level)
        return transaction_amount * bonus_rate
        
    async def _get_bonus_rate(self, noble_level: int) -> Decimal:
        rates = {
            1: Decimal('0.01'),  # Knight
            2: Decimal('0.02'),  # Baron
            3: Decimal('0.03'),  # Count
            4: Decimal('0.04')   # Duke
        }
        return rates.get(noble_level, Decimal('0'))

    async def calculate_weekly_bonus(self, user_id: int) -> Decimal:
        try:
            total_investment = await self._get_total_investment(user_id)
            rank = await self._get_user_rank(user_id)
            base_bonus = total_investment * self.bonus_rates[rank]
            
            # Applica moltiplicatori performance
            performance_multiplier = await self._calculate_performance_multiplier(user_id)
            final_bonus = base_bonus * performance_multiplier
            
            logger.info(f"Bonus calcolato per user {user_id}: {final_bonus}")
            return final_bonus
        except Exception as e:
            logger.error(f"Error calculating bonus: {str(e)}")
            return Decimal('0')

    async def _get_total_investment(self, user_id: int) -> Decimal:
        #Implementation to get total investment for a user.  Replace with your actual logic.
        raise NotImplementedError

    async def _get_user_rank(self, user_id: int) -> str:
        #Implementation to get user rank. Replace with your actual logic.
        raise NotImplementedError

    async def _calculate_performance_multiplier(self, user_id: int) -> Decimal:
        #Implementation to calculate performance multiplier. Replace with your actual logic.
        raise NotImplementedError