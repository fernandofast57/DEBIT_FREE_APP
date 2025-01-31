from decimal import Decimal, ROUND_DOWN
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.models import db, NobleRelation, BonusRate, User, GoldAccount, GoldReward
from app.utils.logging_config import get_logger
from app.services.blockchain_service import BlockchainService
from app.utils.errors import InvalidRankError, InsufficientBalanceError
from datetime import datetime
from typing import Dict

logger = get_logger(__name__)

class BonusDistributionService:
    MAX_BONUS_LEVEL = 3

    def __init__(self):
        self._init_bonus_rates()

    def _init_bonus_rates(self):
        """Initialize or verify bonus rates"""
        rates = [
            (1, Decimal('0.007'), 'Bronze'),
            (2, Decimal('0.005'), 'Silver'),
            (3, Decimal('0.005'), 'Gold')
        ]

        for level, rate, name in rates:
            existing = BonusRate.query.filter_by(level=level).first()
            if not existing:
                bonus_rate = BonusRate(level=level, rate=rate, name=name)
                db.session.add(bonus_rate)
        db.session.commit()

    @staticmethod
    def validate_bonus_amount(amount: Decimal) -> bool:
        """Validate bonus amount to ensure it meets minimum requirements

        Args:
            amount: Importo del bonus da validare

        Returns:
            True se l'importo è valido, False altrimenti
        """
        return amount > Decimal('0') and amount.quantize(Decimal('.0001')) == amount

    async def calculate_purchase_bonuses(self, user_id: int, purchase_amount: Decimal) -> dict:
        """Calculate bonuses for a purchase through the network (both upline and downline)

        Args:
            user_id: ID dell'utente che effettua l'acquisto
            purchase_amount: Importo dell'acquisto in oro

        Returns:
            Dictionary con i bonus calcolati per ogni utente della rete
        """
        bonuses = {}

        # Ottimizzazione: Carica utente e relazioni in una singola query
        current_user = await db.session.execute(
            select(User).options(
                joinedload(User.noble_relations)
            ).filter_by(id=user_id)
        ).scalar_one_or_none()

        if not current_user:
            logger.warning(f"Utente {user_id} non trovato")
            return bonuses

        # Calculate upline bonuses (only first 3 levels receive bonuses)
        current_level = 1
        temp_user = current_user
        while temp_user.referrer_id and current_level <= self.MAX_BONUS_LEVEL:
            referrer = await User.query.get(temp_user.referrer_id)
            if referrer:
                rate = self._get_bonus_rate(current_level)
                if rate > 0:
                    bonus_amount = (purchase_amount * rate).quantize(Decimal('0.0001'))
                    bonuses[referrer.id] = {
                        'level': current_level,
                        'amount': bonus_amount,
                        'rate': rate,
                        'type': 'upline'
                    }
            temp_user = referrer
            current_level += 1

        # Calculate downline bonuses (only from first 3 levels)
        downline_relations = await NobleRelation.query.filter(
            NobleRelation.referrer_id == user_id,
            NobleRelation.level <= self.MAX_BONUS_LEVEL
        ).all()

        for relation in downline_relations:
            rate = self._get_bonus_rate(relation.level)
            if rate > 0:
                bonus_amount = (purchase_amount * rate).quantize(Decimal('0.0001'))
                bonuses[user_id] = {
                    'level': relation.level,
                    'amount': bonus_amount,
                    'rate': rate,
                    'type': 'downline'
                }

        return bonuses

    def _get_bonus_rate(self, level: int) -> Decimal:
        """Get bonus rate for a specific level"""
        rates = {
            1: Decimal('0.007'),  # Bronze - 0.7%
            2: Decimal('0.005'),  # Silver - 0.5%
            3: Decimal('0.005')   # Gold - 0.5%
        }
        return rates.get(level, Decimal('0'))

    async def distribute_bonuses(self, bonuses: dict) -> dict:
        """Distribute calculated bonuses to users with validation"""
        distribution_results = {}
        try:
            async with db.session.begin_nested():
                for user_id, bonus_info in bonuses.items():
                    if not self.validate_bonus_amount(bonus_info['amount']):
                        raise ValueError(f"Invalid bonus amount for user {user_id}")
                    
                    user = await User.query.get(user_id)
                    if user:
                        await self._credit_bonus(user, bonus_info['amount'])
                        distribution_results[user_id] = {
                            'status': 'success',
                            'amount': str(bonus_info['amount']),
                            'level': bonus_info['level'],
                            'type': bonus_info['type']
                        }
                        logger.info(f"Credited {bonus_info['type']} bonus {bonus_info['amount']} to user {user_id} at level {bonus_info['level']}")

            await db.session.commit()
            return {'status': 'success', 'distributions': distribution_results}

        except Exception as e:
            logger.error(f"Error distributing bonuses: {str(e)}")
            await db.session.rollback()
            return {'status': 'error', 'error': str(e)}

    async def _credit_bonus(self, user: User, amount: Decimal) -> None:
        """Credit bonus to user's account"""
        gold_account = await GoldAccount.query.filter_by(user_id=user.id).first()
        if not gold_account:
            raise ValueError("Gold account not found for user")
        gold_account.balance += amount
        gold_account.last_updated = datetime.utcnow()


class PremiumDistributionService:
    def __init__(self):
        self.blockchain_service = BlockchainService()
        self._init_premium_rates()
        self._init_thresholds()
        self.operational_wallet = None  # Should be configured during initialization

    def _init_premium_rates(self):
        """Initialize bonus rates with maximum precision for gold calculations"""
        self.bonus_rates = {
            'livello1': Decimal('0.007').quantize(Decimal('0.00001')),  # 0.7%
            'livello2': Decimal('0.005').quantize(Decimal('0.00001')),  # 0.5%
            'livello3': Decimal('0.005').quantize(Decimal('0.00001')),  # 0.5%
            'operational': Decimal('0.05').quantize(Decimal('0.00001'))  # 5%
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

    @staticmethod
    def validate_gold_amount(amount: Decimal) -> Decimal:
        """Standardizza e valida l'importo in oro"""
        # Forza 2 decimali per centesimi di grammo
        validated_amount = Decimal(str(amount)).quantize(Decimal('0.01'))
        if validated_amount <= 0:
            raise ValueError("L'importo del bonus deve essere positivo")
        if validated_amount * 100 != int(validated_amount * 100):
            raise ValueError("L'importo deve essere in centesimi di grammo pieni")
        return validated_amount

    async def distribute_gold_bonus(self, user_id: int, amount: Decimal) -> Dict:
        try:
            amount = self.validate_gold_amount(amount)
            gold_account = await GoldAccount.query.filter_by(user_id=user_id).first()

            if not gold_account:
                raise ValueError("Account oro non trovato")

            previous_balance = gold_account.balance
            gold_account.balance += amount
            gold_account.last_updated = datetime.utcnow()

            await db.session.commit()

            logger.info(f"Bonus oro distribuito: {amount} all'utente {user_id}")
            return {
                "success": True,
                "previous_balance": str(previous_balance),
                "new_balance": str(gold_account.balance),
                "bonus_amount": str(amount)
            }

        except Exception as e:
            logger.error(f"Errore nella distribuzione del bonus: {str(e)}")
            await db.session.rollback()
            raise

    async def distribute_rewards(self, user_id: int, euro_amount: Decimal, fixing_price: Decimal) -> Dict:
        """Distribute both structure and achievement rewards"""
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

                    bonus_gold = (euro_amount * self.bonus_rates[f'livello{level}']).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

                    if bonus_gold > 0:
                        await self._create_and_save_reward(
                            referrer.id,
                            bonus_gold,
                            'structure',
                            level,
                            euro_amount,
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
        if not user or not user.gold_account:
            raise ValueError(f"User {user_id} or their gold account not found")
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
            logger.info(f"Operational fee of {operational_fee_gold}g distributed")

    async def distribute_achievement_reward(self, user_id: int, euro_amount: Decimal, fixing_price: Decimal) -> Dict:
        """Distribute achievement rewards based on thresholds"""
        try:
            user = await User.query.get(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")

            total_volume = await self._calculate_total_volume(user_id)
            achieved_level = None

            for level, threshold in sorted(self.achievement_thresholds.items(), key=lambda x: x[1], reverse=True):
                if total_volume >= threshold:
                    achieved_level = level
                    break

            if not achieved_level:
                return {"status": "no_achievement", "total_volume": str(total_volume)}

            reward_amount = self.achievement_rewards[achieved_level]
            await self._create_and_save_reward(
                user_id,
                reward_amount,
                'achievement',
                0,  # Level 0 for achievements
                euro_amount,
                fixing_price,
                total_volume
            )

            return {
                "status": "success",
                "achievement_level": achieved_level,
                "reward_amount": str(reward_amount),
                "total_volume": str(total_volume)
            }

        except Exception as e:
            logger.error(f"Error in achievement distribution: {str(e)}")
            raise

    async def _calculate_total_volume(self, user_id: int) -> Decimal:
        """Calculate total volume for achievement rewards"""
        # Implementation depends on your specific requirements
        return Decimal('0')  # Placeholder - implement actual calculation