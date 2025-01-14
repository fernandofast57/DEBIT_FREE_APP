# app/services/two_factor_service.py
import pyotp
from app.database import db
from app.models.user import User
import qrcode
import io
import base64
import logging

logger = logging.getLogger(__name__)


class TwoFactorService:

    def __init__(self):
        self.issuer_name = "GoldApp"

    def generate_secret(self) -> str:
        """Genera un nuovo secret per 2FA"""
        return pyotp.random_base32()

    def generate_qr_code(self, email: str, secret: str) -> str:
        """Genera un QR code per il 2FA"""
        try:
            totp = pyotp.TOTP(secret)
            provisioning_uri = totp.provisioning_uri(
                email, issuer_name=self.issuer_name)

            # Crea QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)

            # Converti in immagine
            img = qr.make_image(fill_color="black", back_color="white")

            # Converti in base64
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}"

        except Exception as e:
            logger.error(f"Errore nella generazione QR code: {str(e)}")
            raise

    async def enable_2fa(self, user_id: int) -> dict:
        """Abilita 2FA per un utente"""
        try:
            user = await User.query.get(user_id)
            if not user:
                raise ValueError(f"Utente non trovato: {user_id}")

            secret = self.generate_secret()
            qr_code = self.generate_qr_code(user.email, secret)

            user.two_factor_secret = secret
            user.two_factor_enabled = True
            await db.session.commit()

            return {"secret": secret, "qr_code": qr_code}

        except Exception as e:
            logger.error(f"Errore nell'abilitazione 2FA: {str(e)}")
            await db.session.rollback()
            raise

    def verify_2fa(self, secret: str, token: str) -> bool:
        """Verifica un token 2FA"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token)
        except Exception as e:
            logger.error(f"Errore nella verifica 2FA: {str(e)}")
            return False
