from datetime import datetime
from app import db
from decimal import Decimal
from .models import User

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
    bonus_rate = db.Column(db.Numeric(precision=5, scale=4), nullable=False)
    level = db.Column(db.Integer, nullable=False)

class NobleRelation(db.Model):
    __tablename__ = 'noble_relations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    referrer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    noble_id = db.Column(db.Integer, db.ForeignKey('noble_ranks.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    verification_status = db.Column(db.Enum('to_be_verified', 'verified', 'rejected', name='verification_status_enum'))
    document_type = db.Column(db.String(50))
    document_number = db.Column(db.String(50))
    verification_date = db.Column(db.DateTime)

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='noble_relations')
    referrer = db.relationship('User', foreign_keys=[referrer_id], backref='referrals')
    noble_rank = db.relationship('NobleRank')