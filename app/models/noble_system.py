from decimal import Decimal, ROUND_DOWN
from . import db
from .models import User, NobleRelation, BonusTransaction


class SistemaNobile:
    # Tassi premio in peso oro (grammi)
    TASSI_PREMIO = {
        1: Decimal('0.007'),  # Livello 1: 0.7% del peso acquisito
        2: Decimal('0.005'),  # Livello 2: 0.5% del peso acquisito
        3: Decimal('0.005')  # Livello 3: 0.5% del peso acquisito
    }

    GOLD_WEIGHT_PRECISION = Decimal(
        '0.01')  # Precisione in centesimi di grammo
    MAX_LEVEL = 3

    def __init__(self, db_session):
        self.db = db_session

    async def calculate_bonus(self, user_id: int,
                              gold_weight: Decimal) -> Decimal:
        """Calcola il bonus in peso oro per il livello dell'utente"""
        user = await self.db.query(User).filter_by(id=user_id).first()
        if not user or not user.noble_rank:
            return Decimal('0')

        bonus_rate = self.BONUS_RATES.get(user.noble_rank.level, Decimal('0'))
        return (gold_weight * bonus_rate).quantize(Decimal('0.01'),
                                                   rounding=ROUND_DOWN)
