# app/models/kyc.py
from enum import Enum
from app.database import db
from datetime import datetime


class KYCStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    INCOMPLETE = "incomplete"


class KYCDetail(db.Model):
    __tablename__ = 'kyc_details'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum(KYCStatus), default=KYCStatus.PENDING)
    document_type = db.Column(db.String(50))
    document_number = db.Column(db.String(100))
    verified_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,
                           default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<KYCDetail {self.user_id} - {self.status}>'
