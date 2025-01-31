from decimal import Decimal, ROUND_DOWN
import logging
from datetime import datetime
from typing import Dict, Any
from app.utils.monitoring.gold_metrics import track_distribution_metrics
from app.core.exceptions import TransformationError
from app.models import db
from app.models.models import User, GoldAccount, MoneyAccount, GoldTransformation

logger = logging.getLogger(__name__)

class TransformationService:
    """Gold transformation management service according to official standards"""

    BASE_SPREAD = Decimal('5.0')
    OPERATIONAL_SPREAD = Decimal('1.7')
    MIN_AMOUNT = Decimal('100')
    MAX_AMOUNT = Decimal('100000')

    def __init__(self, db_session):
        self.db = db_session
        self.logger = logger

    def _calculate_spread(self, amount: Decimal) -> Decimal:
        """Calcola spread secondo standard (5% + 1.7%)"""
        return amount * (self.BASE_SPREAD + self.OPERATIONAL_SPREAD) / Decimal('100')

    async def _get_current_fixing_price(self) -> Decimal:
        """Recupera fixing price corrente"""
        # Implementazione mock per esempio
        return Decimal('1800.00')

    def _validate_amount(self, amount: Decimal) -> bool:
        """Valida importo secondo limiti standard"""
        return self.MIN_AMOUNT <= amount <= self.MAX_AMOUNT

    @track_distribution_metrics
    async def execute_transformation(self, user_id: int, euro_amount: Decimal) -> Dict[str, Any]:
        """Esegue trasformazione con validazione completa"""
        start_time = datetime.utcnow()

        try:
            # Standardizza importo euro
            euro_amount = euro_amount.quantize(Decimal('0.01'), rounding=ROUND_DOWN)

            if not self._validate_amount(euro_amount):
                raise TransformationError(f"Amount must be between {self.MIN_AMOUNT} and {self.MAX_AMOUNT} EUR")

            fixing_price = await self._get_current_fixing_price()
            spread = self._calculate_spread(euro_amount)
            net_amount = euro_amount - spread

            # Calcola grammi oro con precisione standard
            gold_grams = (net_amount / fixing_price).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)

            async with self.db.begin():
                user = await self.db.query(User).get(user_id)
                euro_account = await self.db.query(EuroAccount).filter_by(user_id=user_id).first()
                gold_account = await self.db.query(GoldAccount).filter_by(user_id=user_id).first()

                if euro_account.balance < euro_amount:
                    raise TransformationError("Insufficient funds")

                # Aggiorna conti
                euro_account.balance -= euro_amount
                gold_account.balance += gold_grams

                # Registra trasformazione
                transformation = GoldTransformation(
                    user_id=user_id,
                    euro_amount=euro_amount,
                    gold_grams=gold_grams,
                    fixing_price=fixing_price,
                    spread_amount=spread,
                    status='completed'
                )
                self.db.add(transformation)

                await self.db.commit()

                duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                if duration > 1500:  # Standard 1.5s
                    self.logger.warning(f"Slow transformation: {duration}ms")

                return {
                    'status': 'success',
                    'transformation_id': transformation.id,
                    'euro_amount': euro_amount,
                    'gold_grams': gold_grams,
                    'spread': spread,
                    'fixing_price': fixing_price
                }

        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Transformation failed: {str(e)}")
            raise TransformationError(str(e))