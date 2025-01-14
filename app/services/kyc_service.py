# app/services/kyc_service.py
from app.models.kyc import KYCDetail, KYCStatus, DocumentType
from app.database import db
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class KYCService:

    @staticmethod
    async def submit_kyc(user_id: int, document_type: str,
                         document_number: str, document_url: str) -> KYCDetail:
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

            # TODO: Trigger notification
            return kyc_detail

        except Exception as e:
            logger.error(f"Errore durante l'invio KYC: {str(e)}")
            await db.session.rollback()
            raise

    @staticmethod
    async def verify_kyc(kyc_id: int,
                         approved: bool,
                         notes: Optional[str] = None) -> KYCDetail:
        """Verifica una richiesta KYC"""
        try:
            kyc_detail = await KYCDetail.query.get(kyc_id)
            if not kyc_detail:
                raise ValueError(f"KYC non trovato con ID: {kyc_id}")

            kyc_detail.status = KYCStatus.APPROVED.value if approved else KYCStatus.REJECTED.value
            kyc_detail.verification_date = datetime.utcnow()
            kyc_detail.notes = notes

            await db.session.commit()

            # TODO: Send notification to user
            return kyc_detail

        except Exception as e:
            logger.error(f"Errore durante la verifica KYC: {str(e)}")
            await db.session.rollback()
            raise

    @staticmethod
    async def get_user_kyc_status(user_id: int) -> Optional[KYCDetail]:
        """Recupera lo stato KYC dell'utente"""
        try:
            return await KYCDetail.query.filter_by(user_id=user_id).first()
        except Exception as e:
            logger.error(f"Errore nel recupero stato KYC: {str(e)}")
            raise
