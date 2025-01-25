
from decimal import Decimal, ROUND_DOWN
from typing import Dict, Optional
from datetime import datetime
import logging
from app.models.models import User, GoldReward, db
from app.utils.logging_config import get_logger

logger = get_logger(__name__)
from app.services.blockchain_service import BlockchainService
from app.utils.errors import InvalidRankError, InsufficientBalanceError

class BonusDistributionService:
    def __init__(self):
        self.blockchain_service = BlockchainService()
        self._init_bonus_rates()
        self._init_thresholds()
        
    def _init_bonus_rates(self):
        """Initialize bonus rates with maximum precision for gold calculations"""
        self.bonus_rates = {
            'count': Decimal('0.007').quantize(Decimal('0.00001')),   # Level 1 
            'duke': Decimal('0.005').quantize(Decimal('0.00001')),    # Level 2
            'prince': Decimal('0.005').quantize(Decimal('0.00001')),  # Level 3
            'operational': Decimal('0.05').quantize(Decimal('0.00001'))
        }
        
        # Validazione tassi bonus
        if not all(rate > 0 for rate in self.bonus_rates.values()):
            raise ValueError("Tutti i tassi bonus devono essere positivi")
        
    def _init_thresholds(self):
        """Initialize achievement thresholds and rewards"""
        self.achievement_thresholds = {
            'bronze': Decimal('5000'),
            'silver': Decimal('10000'),
            'gold': Decimal('25000'),
            'platinum': Decimal('50000')
        }
        
        self.achievement_rewards = {
            'bronze': Decimal('0.1000'),
            'silver': Decimal('0.2500'),
            'gold': Decimal('0.5000'),
            'platinum': Decimal('1.0000')
        }

    async def distribute_rewards(self, user_id: int, euro_amount: Decimal, fixing_price: Decimal) -> Dict:
        """Distribute both structure and achievement rewards with error handling"""
        try:
            if not isinstance(euro_amount, Decimal):
                euro_amount = Decimal(str(euro_amount))
            if not isinstance(fixing_price, Decimal):
                fixing_price = Decimal(str(fixing_price))
                
            structure_rewards = await self.distribute_structure_bonus(user_id, euro_amount, fixing_price)
            achievement_reward = await self.distribute_achievement_reward(user_id, euro_amount, fixing_price)
            
            return {
                'structure_rewards': structure_rewards,
                'achievement_reward': achievement_reward,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except InvalidRankError as e:
            logger.error(f"Invalid rank error for user {user_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error distributing rewards for user {user_id}: {str(e)}")
            raise

    async def distribute_structure_bonus(self, user_id: int, euro_amount: Decimal, fixing_price: Decimal) -> Dict:
        """Distribute structure bonus with improved validation"""
        distribution_results = {}
        async with db.session.begin_nested():
            try:
                current_user = await User.query.get(user_id)
                if not current_user:
                    raise ValueError(f"User {user_id} not found")
                
                level = 1
                while current_user.referrer_id and level <= 3:
                    referrer = await User.query.get(current_user.referrer_id)
                    if not referrer:
                        break
                        
                    bonus_euro = (euro_amount * self.bonus_rates[f'level_{level}']).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
                    bonus_gold = (bonus_euro / fixing_price).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)
                    
                    if bonus_gold > 0:
                        await self._create_and_save_reward(
                            referrer.id, 
                            bonus_gold,
                            'structure',
                            level,
                            bonus_euro,
                            fixing_price,
                            euro_amount
                        )
                        
                        distribution_results[referrer.id] = {
                            'level': level,
                            'gold_amount': float(bonus_gold)
                        }
                    
                    current_user = referrer
                    level += 1
                
                await self._handle_operational_fee(euro_amount, fixing_price)
                await db.session.commit()
                
            except Exception as e:
                logger.error(f"Error in structure bonus distribution: {str(e)}")
                await db.session.rollback()
                raise
                
        return distribution_results

    async def _create_and_save_reward(self, user_id: int, gold_amount: Decimal, 
                                    reward_type: str, level: int, euro_amount: Decimal, 
                                    fixing_price: Decimal, threshold_reached: Decimal) -> None:
        """Helper method to create and save rewards"""
        reward = GoldReward(
            user_id=user_id,
            gold_amount=gold_amount,
            reward_type=reward_type,
            level=level,
            euro_amount=euro_amount,
            fixing_price=fixing_price,
            threshold_reached=threshold_reached
        )
        db.session.add(reward)
        
        user = await User.query.get(user_id)
        user.gold_account.balance += gold_amount
        
    async def _handle_operational_fee(self, euro_amount: Decimal, fixing_price: Decimal) -> None:
        """Handle operational fee distribution"""
        if not self.operational_wallet:
            logger.warning("Operational wallet not configured")
            return
            
        operational_fee_euro = (euro_amount * self.bonus_rates['operational']).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        operational_fee_gold = (operational_fee_euro / fixing_price).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)
        
        if operational_fee_gold > 0:
            reward = GoldReward(
                user_id=None,
                gold_amount=operational_fee_gold,
                reward_type='operational',
                euro_amount=operational_fee_euro,
                fixing_price=fixing_price,
                threshold_reached=euro_amount
            )
            db.session.add(reward)
            logger.info(f"Operational fee of {operational_fee_gold}g distributed to {self.operational_wallet}")

    async def calculate_bonus(self, user_id: int, transaction_amount: Decimal) -> Decimal:
        """Calculate user bonus with validation"""
        try:
            user = await User.query.get(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
                
            if not user.noble_rank:
                return Decimal('0')
                
            bonus_rate = await self._get_bonus_rate(user.noble_rank.level)
            return (transaction_amount * bonus_rate).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)
            
        except Exception as e:
            logger.error(f"Error calculating bonus: {str(e)}")
            raise

    async def _get_bonus_rate(self, noble_level: int) -> Decimal:
        """Get bonus rate for noble level with validation"""
        rates = {
            1: Decimal('0.01'),  # Knight
            2: Decimal('0.02'),  # Baron
            3: Decimal('0.03'),  # Count
            4: Decimal('0.04')   # Duke
        }
        
        if noble_level not in rates:
            raise InvalidRankError(f"Invalid noble level: {noble_level}")
            
        return rates[noble_level]
