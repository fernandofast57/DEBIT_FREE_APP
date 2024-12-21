
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
    date = db.Column(db.DateTime, default=datetime.utcnow)
    entry_type = db.Column(db.String(50), nullable=False)  # purchase, sale, commission, bonus
    amount_eur = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    amount_gold = db.Column(db.Numeric(precision=10, scale=4))
    gold_price = db.Column(db.Numeric(precision=10, scale=2))
    reference_id = db.Column(db.String(100))
    notes = db.Column(db.String(500))
