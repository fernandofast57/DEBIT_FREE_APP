
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class GoldReward(db.Model):
    __tablename__ = 'gold_rewards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    gold_amount = db.Column(db.Numeric(precision=10, scale=4), nullable=False)  # Precision to 4 decimal places
    reward_type = db.Column(db.String(50), nullable=False)  # 'structure' or 'achievement'
    level = db.Column(db.Integer)  # 1, 2, or 3 for structure rewards
    threshold_reached = db.Column(db.Numeric(precision=10, scale=2))  # Investment threshold that triggered reward
    euro_amount = db.Column(db.Numeric(precision=10, scale=2))  # Original euro amount
    fixing_price = db.Column(db.Numeric(precision=10, scale=2))  # Gold fixing price used
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='gold_rewards')
