from datetime import datetime
from decimal import Decimal
from app.models import db

class GoldInventory(db.Model):
    __tablename__ = 'gold_inventory'

    id = db.Column(db.Integer, primary_key=True)
    grams = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    purchase_price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='available')  # available, reserved, distributed

class AccountingEntry(db.Model):
    __tablename__ = 'accounting_entries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 4), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    referral_level = db.Column(db.Integer)  # 1, 2, o 3 per bonus referral
    parent_transaction_id = db.Column(db.Integer, db.ForeignKey('accounting_entries.id'))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relazione per tracciare la catena di referral
    parent_transaction = db.relationship('AccountingEntry', remote_side=[id],
                                       backref=db.backref('child_transactions'))