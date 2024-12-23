
from datetime import datetime
from app import db
from decimal import Decimal
from .models import User, NobleRank, NobleRelation

class NobleSystem:
    def __init__(self, db_session):
        self.db = db_session
        
    async def calculate_bonus(self, user_id: int, transaction_amount: Decimal) -> Decimal:
        user = await self.db.query(User).filter_by(id=user_id).first()
        if not user or not user.noble_rank:
            return Decimal('0')
        return transaction_amount * user.noble_rank.bonus_rate
