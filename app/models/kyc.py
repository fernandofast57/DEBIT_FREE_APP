# app/models/kyc.py
from app.database import db
from datetime import datetime
from enum import Enum


class DocumentType(Enum):
    PASSPORT = "passport"
    ID_CARD = "id_card"
    DRIVERS_LICENSE = "drivers_license"


class KYCStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class KYCDetail(db.Model):
    __tablename__ = 'kyc_details'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)
    document_number = db.Column(db.String(100), nullable=False)
    document_url = db.Column(db.String(255))
    status = db.Column(db.String(20), default=KYCStatus.PENDING.value)
    verification_date = db.Column(db.DateTime)
    submitted_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

    # Relazioni
    user = db.relationship('User',
                           backref=db.backref('kyc_details', lazy=True))

    def __repr__(self):
        return f'<KYCDetail {self.id} - User {self.user_id} - Status {self.status}>'
