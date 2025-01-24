from decimal import Decimal
from . import db
from .models import User, NobleRank, NobleRelation, BonusTransaction

class NobleSystem:
    def __init__(self, db_session):
        self.db = db_session
        
    async def calculate_bonus(self, user_id: int, transaction_amount: Decimal) -> Decimal:
        user = await self.db.query(User).filter_by(id=user_id).first()
        if not user or not user.noble_rank:
            return Decimal('0')
        return transaction_amount * user.noble_rank.bonus_rate

class NobleRelation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    noble_rank_id = db.Column(db.Integer, db.ForeignKey('noble_ranks.id'))
    verification_status = db.Column(db.String(50))
    status = db.Column(db.String(50))