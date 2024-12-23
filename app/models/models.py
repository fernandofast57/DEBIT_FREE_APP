
from app import db
from datetime import datetime

class NobleRelation(db.Model):
    __tablename__ = 'noble_relations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    noble_rank_id = db.Column(db.Integer, db.ForeignKey('noble_ranks.id'), nullable=False)
    verification_status = db.Column(db.String(20), default='to_be_verified')
    verification_date = db.Column(db.DateTime)
    document_type = db.Column(db.String(50))
    document_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
