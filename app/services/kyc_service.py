# app/services/kyc_service.py
from app.models.models import KYCDetail, User
from app.database import db
from datetime import datetime
from typing import Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# Definizione degli enum qui dato che li abbiamo rimossi da kyc.py
class DocumentType(Enum):
    PASSPORT = "passport"
    ID_CARD = "id_card"
    DRIVERS_LICENSE = "drivers_license"


class KYCStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class KYCService:

    @staticmethod
    async def submit_kyc(user_id: int, document_type: str,
                         document_number: str, document_url: str) -> dict:
        """Invia una nuova richiesta KYC"""
        try:
            if not DocumentType.__members__.get(document_type.upper()):
                raise ValueError(f"Tipo documento non valido: {document_type}")

            kyc_detail = KYCDetail(user_id=user_id,
                                   document_type=document_type,
                                   document_number=document_number,
                                   document_url=document_url,
                                   status=KYCStatus.PENDING.value)

            db.session.add(kyc_detail)
            await db.session.commit()

            return {
                'status': 'success',
                'kyc_id': kyc_detail.id,
                'message': 'KYC submitted successfully'
            }

        except Exception as e:
            logger.error(f"Errore durante l'invio KYC: {str(e)}")
            await db.session.rollback()
            raise

    @staticmethod
    async def verify_kyc(kyc_id: int,
                         approved: bool,
                         notes: Optional[str] = None) -> dict:
        """Verifica una richiesta KYC"""
        try:
            kyc_detail = await KYCDetail.query.get(kyc_id)
            if not kyc_detail:
                raise ValueError(f"KYC non trovato con ID: {kyc_id}")

            kyc_detail.status = KYCStatus.APPROVED.value if approved else KYCStatus.REJECTED.value
            kyc_detail.verification_date = datetime.utcnow()
            kyc_detail.notes = notes

            # Aggiorna anche lo stato KYC dell'utente
            user = await User.query.get(kyc_detail.user_id)
            if user:
                user.kyc_verified = approved
                user.kyc_verified_date = datetime.utcnow(
                ) if approved else None

            await db.session.commit()

            return {
                'status': 'success',
                'message': 'KYC verification completed',
                'kyc_status': kyc_detail.status
            }

        except Exception as e:
            logger.error(f"Errore durante la verifica KYC: {str(e)}")
            await db.session.rollback()
            raise

    @staticmethod
    async def get_user_kyc_status(user_id: int) -> dict:
        """Recupera lo stato KYC dell'utente"""
        try:
            kyc_detail = await KYCDetail.query.filter_by(
                user_id=user_id).order_by(KYCDetail.submitted_date.desc()
                                          ).first()

            return {
                'status':
                'success',
                'kyc_status':
                kyc_detail.status if kyc_detail else 'not_submitted',
                'submission_date':
                kyc_detail.submitted_date.isoformat() if kyc_detail else None,
                'verification_date':
                kyc_detail.verification_date.isoformat()
                if kyc_detail and kyc_detail.verification_date else None
            }

        except Exception as e:
            logger.error(f"Errore nel recupero stato KYC: {str(e)}")
            raise
