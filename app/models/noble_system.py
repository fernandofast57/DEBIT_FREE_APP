
from datetime import datetime
from app import db
from datetime import datetime

class BonusTransaction(db.Model):
    __tablename__ = 'bonus_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('bonus_transactions', lazy=True))
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
