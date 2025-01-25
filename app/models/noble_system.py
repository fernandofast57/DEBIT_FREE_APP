
from decimal import Decimal
from . import db
from .models import User, NobleRelation, BonusTransaction

class NobleRank(db.Model):
    __tablename__ = 'noble_ranks'

    id = db.Column(db.Integer, primary_key=True)
    rank_name = db.Column(db.String(50), nullable=False)
    bonus_rate = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    min_investment = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    level = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<NobleRank {self.rank_name} (Bonus Rate: {self.bonus_rate})>"

class NobleSystem:
    def __init__(self, db_session):
        self.db = db_session

    async def calculate_bonus(self, user_id: int, transaction_amount: Decimal) -> Decimal:
        user = await self.db.query(User).filter_by(id=user_id).first()
        if not user or not user.noble_rank:
            return Decimal('0')
        return transaction_amount * user.noble_rank.bonus_rate
