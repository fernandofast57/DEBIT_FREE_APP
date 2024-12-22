from datetime import datetime
from app import db
from decimal import Decimal

class NobleSystem:
    def __init__(self, db_session):
        self.db = db_session
        
    async def calculate_bonus(self, user_id: int, transaction_amount: Decimal) -> Decimal:
        user = await self.db.query(User).filter_by(id=user_id).first()
        if not user or not user.noble_rank:
            return Decimal('0')
        return transaction_amount * user.noble_rank.bonus_rate

class NobleRank(db.Model):
    __tablename__ = 'noble_ranks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False, unique=True)
    bonus_rate = db.Column(db.Numeric(precision=5, scale=4), nullable=False)  # es. 0.007 per 0.7%
    level = db.Column(db.Integer, nullable=False)  # 1 = Nobile, 2 = Visconte, 3 = Conte

class NobleRelation(db.Model):
    __tablename__ = 'noble_relations'
    
    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    referred_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rank_id = db.Column(db.Integer, db.ForeignKey('noble_ranks.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relazioni
    rank = db.relationship('NobleRank')
    referrer = db.relationship('User', foreign_keys=[referrer_id], backref='referrals')
    referred = db.relationship('User', foreign_keys=[referred_id], backref='upline')

class BonusTransaction(db.Model):
    __tablename__ = 'bonus_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    bonus_amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    rank_id = db.Column(db.Integer, db.ForeignKey('noble_ranks.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relazioni
    user = db.relationship('User', backref='bonus_transactions')
    rank = db.relationship('NobleRank')
