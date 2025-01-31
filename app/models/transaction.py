
from app.models import db

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    operation_type = db.Column(db.String(50))  # ['gold_purchase', 'gold_sale', 'gold_transfer']
    operation_status = db.Column(db.String(50), default='started')  # ['started', 'processing', 'completed', 'failed']
    gold_quantity = db.Column(db.Numeric(precision=10, scale=4))
    gold_price = db.Column(db.Numeric(precision=10, scale=2))
    creation_date = db.Column(db.DateTime, default=db.func.current_timestamp())
