from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    money_account = db.relationship('MoneyAccount', back_populates='user', uselist=False)
    gold_account = db.relationship('GoldAccount', back_populates='user', uselist=False)
    
    def __repr__(self):
        return f"<User {self.username}>"

class MoneyAccount(db.Model):
    __tablename__ = 'money_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Numeric(precision=10, scale=2), default=Decimal('0.00'))
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='money_account')
    
    def __repr__(self):
        return f"<MoneyAccount {self.balance}>"

class GoldAccount(db.Model):
    __tablename__ = 'gold_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Numeric(precision=10, scale=4), default=Decimal('0.0000'))
    pao_active = db.Column(db.Boolean, default=False)
    ppo_active = db.Column(db.Boolean, default=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='gold_account')
    
    allocations = db.relationship('GoldAllocation', back_populates='gold_account')
    
    def __repr__(self):
        return f"<GoldAccount {self.user.username}, {self.balance:.4f}g>"

class NobleRank(db.Model):
    __tablename__ = 'noble_ranks'
    
    id = db.Column(db.Integer, primary_key=True)
    rank_name = db.Column(db.String(50), nullable=False, unique=True)
    bonus_rate = db.Column(db.Numeric(precision=5, scale=4), nullable=False)
    min_investment = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    level = db.Column(db.Integer, nullable=False)

class NobleRelation(db.Model):
    __tablename__ = 'noble_relations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    noble_rank_id = db.Column(db.Integer, db.ForeignKey('noble_ranks.id'), nullable=False)
    verification_status = db.Column(db.Enum('to_be_verified', 'verified', 'rejected', name='verification_status_enum'), default='to_be_verified')
    verification_date = db.Column(db.DateTime)
    document_type = db.Column(db.String(50))
    document_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='noble_relations')
    noble_rank = db.relationship('NobleRank')

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    status = db.Column(db.Enum('to_be_verified', 'verified', 'rejected', name='transaction_status_enum'), default='to_be_verified')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='transactions')

class GoldTransformation(db.Model):
    __tablename__ = 'gold_transformations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    euro_amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    gold_grams = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    fixing_price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    fee_amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='gold_transformations')

class GoldBar(db.Model):
    __tablename__ = 'gold_bars'
    
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(50), unique=True, nullable=False)
    weight_grams = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    status = db.Column(db.Enum('available', 'reserved', 'distributed', name='gold_bar_status_enum'), default='available') #Corrected based on intention
    location = db.Column(db.String(100))
    
    allocations = db.relationship('GoldAllocation', back_populates='gold_bar')

    def __repr__(self):
        return f"<GoldBar {self.serial_number}, {self.weight_grams:.4f}g, {self.status}>"

class GoldAllocation(db.Model):
    __tablename__ = 'gold_allocations'
    
    id = db.Column(db.Integer, primary_key=True)
    grams_allocated = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    
    gold_bar_id = db.Column(db.Integer, db.ForeignKey('gold_bars.id'))
    gold_account_id = db.Column(db.Integer, db.ForeignKey('gold_accounts.id'))
    
    gold_bar = db.relationship('GoldBar', back_populates='allocations')
    gold_account = db.relationship('GoldAccount', back_populates='allocations')
    
    def __repr__(self):
        return f"<GoldAllocation {self.grams_allocated:.4f}g on Bar {self.gold_bar.serial_number}>"