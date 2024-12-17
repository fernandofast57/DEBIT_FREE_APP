
from datetime import datetime
from decimal import Decimal
from typing import Optional
from app import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    noble_rank = db.Column(db.String(50), default='noble', index=True)
    blockchain_address = db.Column(db.String(42), index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships with type hints
    money_account: 'MoneyAccount' = db.relationship('MoneyAccount', backref='user', uselist=False)
    gold_account: 'GoldAccount' = db.relationship('GoldAccount', backref='user', uselist=False)
    
    def check_rank_promotion(self) -> bool:
        """Verifica e aggiorna il rank dell'utente"""
        from app import Config
        
        total_volume = self.get_total_volume()
        for rank, requirements in Config.NOBLE_RANKS.items():
            if total_volume >= requirements['min_volume']:
                if rank != self.noble_rank:
                    self.noble_rank = rank
                    db.session.commit()
                    return True
        return False

    def get_commission_rate(self) -> Decimal:
        """Returns commission rate based on noble rank"""
        from app import Config
        return Decimal(str(Config.NOBLE_RANKS[self.noble_rank]['commission']))

    @staticmethod
    def is_valid_blockchain_address(address: str) -> bool:
        """Validate Ethereum address format"""
        return bool(address and len(address) == 42 and address.startswith('0x'))

class MoneyAccount(db.Model):
    __tablename__ = 'money_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    balance = db.Column(db.Numeric(10, 2), default=0)
    recurring_amount = db.Column(db.Numeric(10, 2))
    last_transfer_at = db.Column(db.DateTime, index=True)
