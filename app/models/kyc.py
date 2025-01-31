
from enum import Enum
from datetime import datetime
from sqlalchemy.orm import validates
from app.database import db
from sqlalchemy.exc import SQLAlchemyError
from app.utils.logging_config import logger

class StatoKYC(Enum):
    IN_ATTESA = "in_attesa"
    APPROVATO = "approvato"
    RIFIUTATO = "rifiutato"
    INCOMPLETO = "incompleto"

class DocumentType(Enum):
    PASSPORT = "passport"
    ID_CARD = "id_card"
    DRIVERS_LICENSE = "drivers_license"

class KYCDetail(db.Model):
    __tablename__ = 'kyc_details'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum(KYCStatus), default=KYCStatus.PENDING)
    document_type = db.Column(db.Enum(DocumentType), nullable=False)
    document_number = db.Column(db.String(100), nullable=False)
    document_url = db.Column(db.String(255))
    verified_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='kyc_documents', foreign_keys=[user_id])

    @validates('document_number')
    def validate_document_number(self, key, number):
        if not number:
            raise ValueError('Numero documento richiesto')
        if len(number) < 5:
            raise ValueError('Numero documento troppo corto')
        return number

    @validates('document_type')
    def validate_document_type(self, key, doc_type):
        if not doc_type:
            raise ValueError('Tipo documento richiesto')
        if not isinstance(doc_type, DocumentType):
            raise ValueError('Tipo documento non valido')
        return doc_type

    def __repr__(self):
        return f'<KYCDetail {self.user_id} - {self.status}>'
