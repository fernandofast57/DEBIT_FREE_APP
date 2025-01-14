# tests/unit/test_kyc_service.py
import pytest
from datetime import datetime
from app.services.kyc_service import KYCService
from app.models.kyc import KYCDetail, KYCStatus


@pytest.mark.asyncio
async def test_submit_kyc(app, test_user):
    async with app.app_context():
        service = KYCService()
        result = await service.submit_kyc(
            test_user.id,
            document_type="passport",
            document_number="AB123456",
            document_url="https://example.com/doc.pdf")

        assert result['status'] == 'success'
        assert 'kyc_id' in result

        # Verifica nel database
        kyc = await KYCDetail.query.get(result['kyc_id'])
        assert kyc.user_id == test_user.id
        assert kyc.document_type == "passport"
        assert kyc.status == KYCStatus.PENDING.value


@pytest.mark.asyncio
async def test_verify_kyc(app, test_user, test_admin):
    async with app.app_context():
        service = KYCService()

        # Prima submit
        submit_result = await service.submit_kyc(
            test_user.id,
            document_type="passport",
            document_number="AB123456",
            document_url="https://example.com/doc.pdf")

        # Poi verifica
        verify_result = await service.verify_kyc(submit_result['kyc_id'],
                                                 approved=True,
                                                 notes="All documents valid")

        assert verify_result['status'] == 'success'

        # Verifica nel database
        kyc = await KYCDetail.query.get(submit_result['kyc_id'])
        assert kyc.status == KYCStatus.APPROVED.value
        assert kyc.verification_date is not None


@pytest.mark.asyncio
async def test_reject_invalid_kyc(app, test_user):
    async with app.app_context():
        service = KYCService()

        # Submit con documento invalido
        result = await service.submit_kyc(test_user.id,
                                          document_type="invalid_type",
                                          document_number="123",
                                          document_url="")

        assert result['status'] == 'error'
        assert 'invalid document type' in result['message'].lower()
