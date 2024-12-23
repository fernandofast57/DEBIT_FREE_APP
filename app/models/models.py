from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app.models.noble_system import NobleRank

db = SQLAlchemy()

class MoneyAccount(db.Model):
    __tablename__ = 'money_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, default=0.0)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='money_account')
    
    def __repr__(self):
        return f"<MoneyAccount {self.balance}>"

class GoldAccount(db.Model):
    __tablename__ = 'gold_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, default=0.0)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='gold_account')
    
    allocations = db.relationship('GoldAllocation', back_populates='gold_account')
    
    def __repr__(self):
        return f"<GoldAccount {self.user.username}, {self.balance:.2f}g>"

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='transactions')

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

class NobleRelation(db.Model):
    __tablename__ = 'noble_relations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    noble_id = db.Column(db.Integer, db.ForeignKey('noble_ranks.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GoldReward(db.Model):
    __tablename__ = 'gold_rewards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    gold_amount = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    reward_type = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Integer)
    threshold_reached = db.Column(db.Numeric(precision=10, scale=2))
    euro_amount = db.Column(db.Numeric(precision=10, scale=2))
    fixing_price = db.Column(db.Numeric(precision=10, scale=2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='gold_rewards')
class GoldBar(db.Model):
    __tablename__ = 'gold_bars'
    
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(50), unique=True, nullable=False)
    weight_grams = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='in_stock')
    location = db.Column(db.String(100), nullable=True)
    
    allocations = db.relationship('GoldAllocation', back_populates='gold_bar')

    def __repr__(self):
        return f"<GoldBar {self.serial_number}, {self.weight_grams}g, {self.status}>"

class GoldAllocation(db.Model):
    __tablename__ = 'gold_allocations'
    
    id = db.Column(db.Integer, primary_key=True)
    grams_allocated = db.Column(db.Float, nullable=False)
    
    gold_bar_id = db.Column(db.Integer, db.ForeignKey('gold_bars.id'))
    gold_account_id = db.Column(db.Integer, db.ForeignKey('gold_accounts.id'))
    
    gold_bar = db.relationship('GoldBar', back_populates='allocations')
    gold_account = db.relationship('GoldAccount', back_populates='allocations')
    
    def __repr__(self):
        return f"<GoldAllocation {self.grams_allocated:.2f}g on Bar {self.gold_bar.serial_number}>"
