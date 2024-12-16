
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from decimal import Decimal

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    blockchain_address = db.Column(db.String(42))  # Lunghezza indirizzo Ethereum
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relazioni
    money_account = db.relationship('MoneyAccount', backref='user', uselist=False)
    gold_account = db.relationship('GoldAccount', backref='user', uselist=False)
    transactions = db.relationship('Transaction', backref='user')
    gold_transformations = db.relationship('GoldTransformation', backref='user')

    def __repr__(self):
        return f'<User {self.email}>'

class MoneyAccount(db.Model):
    __tablename__ = 'money_accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    balance = db.Column(db.Numeric(precision=10, scale=2), default=0)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MoneyAccount {self.user_id}: {self.balance}>'

class GoldAccount(db.Model):
    __tablename__ = 'gold_accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    balance = db.Column(db.Numeric(precision=10, scale=4), default=0)  # 4 decimali per i grammi
    last_update = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<GoldAccount {self.user_id}: {self.balance}g>'

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'deposit', 'withdrawal'
    status = db.Column(db.String(20), nullable=False)  # 'pending', 'completed', 'failed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Transaction {self.id}: {self.amount} {self.type}>'

class GoldTransformation(db.Model):
    __tablename__ = 'gold_transformations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    euro_amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    gold_grams = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    fixing_price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<GoldTransformation {self.id}: €{self.euro_amount} -> {self.gold_grams}g>'
