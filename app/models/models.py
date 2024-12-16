
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

# ... rest of the models code stays the same ...
