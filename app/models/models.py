
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    blockchain_address = db.Column(db.String(42), unique=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    money_account = db.relationship('MoneyAccount', backref='user', uselist=False)
    gold_account = db.relationship('GoldAccount', backref='user', uselist=False)
    noble_rank = db.relationship('NobleRank', backref='users')

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
