
from app.database import db, Base
from datetime import datetime

class WeeklyDistributionLog(db.Model):
    __tablename__ = 'weekly_distribution_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    processing_date = db.Column(db.DateTime, default=datetime.utcnow)
    fixing_price = db.Column(db.Numeric)
    total_euro_processed = db.Column(db.Numeric)
    total_gold_distributed = db.Column(db.Numeric)
    total_affiliate_bonus = db.Column(db.Numeric)
    users_processed = db.Column(db.Integer)
    status = db.Column(db.String)
    error_details = db.Column(db.JSON, nullable=True)

class DistributionSnapshot(db.Model):
    __tablename__ = 'distribution_snapshots'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    snapshot_data = db.Column(db.JSON)
    restored = db.Column(db.Boolean, default=False)
