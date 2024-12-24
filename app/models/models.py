
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Enum
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    bonus_transactions = relationship('BonusTransaction', back_populates='user', cascade='all, delete-orphan')
    rewards = relationship('GoldReward', back_populates='user', overlaps="gold_rewards")
    gold_rewards = relationship('GoldReward', back_populates='user')
    money_account = db.relationship('MoneyAccount', back_populates='user', uselist=False)
    gold_account = db.relationship('GoldAccount', back_populates='user', uselist=False)
    transactions = db.relationship('Transaction', back_populates='user')
    gold_transformations = db.relationship('GoldTransformation', back_populates='user')
    noble_relations = db.relationship('NobleRelation', back_populates='user')

    def __repr__(self):
        return f"<User {self.username}>"

class BonusTransaction(db.Model):
    __tablename__ = 'bonus_transactions'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = relationship('User', back_populates='bonus_transactions')

    def __repr__(self):
        return f"<BonusTransaction {self.amount}>"

# [Rest of your models remain the same...]
