# tests/unit/test_two_factor_service.py
import pytest
from app.services.two_factor_service import TwoFactorService
import pyotp


@pytest.mark.asyncio
async def test_enable_2fa(app, test_user):
    async with app.app_context():
        service = TwoFactorService()
        result = await service.enable_2fa(test_user.id)

        assert 'secret' in result
        assert 'qr_code' in result
        assert result['qr_code'].startswith('data:image/png;base64,')

        # Verifica che il secret sia stato salvato
        test_user = await User.query.get(test_user.id)
        assert test_user.two_factor_secret == result['secret']
        assert test_user.two_factor_enabled is True


def test_verify_valid_2fa_token(app):
    service = TwoFactorService()
    secret = service.generate_secret()

    # Genera un token valido
    totp = pyotp.TOTP(secret)
    token = totp.now()

    assert service.verify_2fa(secret, token) is True


def test_verify_invalid_2fa_token(app):
    service = TwoFactorService()
    secret = service.generate_secret()

    # Token invalido
    assert service.verify_2fa(secret, '000000') is False


@pytest.mark.asyncio
async def test_2fa_qr_code_generation(app, test_user):
    async with app.app_context():
        service = TwoFactorService()
        result = await service.enable_2fa(test_user.id)

        assert 'qr_code' in result
        qr_code = result['qr_code']

        # Verifica il formato del QR code
        assert qr_code.startswith('data:image/png;base64,')
        assert len(qr_code) > 100  # QR code non vuoto
