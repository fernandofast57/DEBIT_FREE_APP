# tests/integration/test_auth_flow.py
import pytest
from app.models.kyc import KYCStatus


@pytest.mark.asyncio
async def test_complete_auth_flow(client, test_user):
    """Test del flusso completo di autenticazione con 2FA e KYC"""
    # 1. Login
    login_response = await client.post('/auth/login',
                                       json={
                                           'user_id': test_user.id,
                                           'device_id': 'test_device'
                                       })
    assert login_response.status_code == 200
    token = login_response.json['token']

    # 2. Abilita 2FA
    headers = {'Authorization': f'Bearer {token}'}
    enable_2fa_response = await client.post('/auth/2fa/enable',
                                            headers=headers)
    assert enable_2fa_response.status_code == 200
    assert 'qr_code' in enable_2fa_response.json

    # 3. Submit KYC
    kyc_data = {
        'document_type': 'passport',
        'document_number': 'AB123456',
        'document_url': 'https://example.com/doc.pdf'
    }
    kyc_response = await client.post('/auth/kyc/submit',
                                     json=kyc_data,
                                     headers=headers)
    assert kyc_response.status_code == 200

    # 4. Verifica stato KYC
    kyc_status_response = await client.get('/auth/kyc/status', headers=headers)
    assert kyc_status_response.status_code == 200
    assert kyc_status_response.json['kyc_status'] == KYCStatus.PENDING.value


@pytest.mark.asyncio
async def test_auth_with_invalid_2fa(client, test_user):
    """Test di autenticazione con 2FA invalido"""
    # Setup 2FA
    login_response = await client.post('/auth/login',
                                       json={
                                           'user_id': test_user.id,
                                           'device_id': 'test_device'
                                       })
    token = login_response.json['token']
    headers = {'Authorization': f'Bearer {token}'}

    await client.post('/auth/2fa/enable', headers=headers)

    # Prova verifica con token invalido
    verify_response = await client.post('/auth/2fa/verify',
                                        json={'token': '000000'},
                                        headers=headers)
    assert verify_response.status_code == 400
    assert 'Invalid token' in verify_response.json['message']


@pytest.mark.asyncio
async def test_kyc_submission_validation(client, test_user):
    """Test della validazione dei dati KYC"""
    # Login
    login_response = await client.post('/auth/login',
                                       json={
                                           'user_id': test_user.id,
                                           'device_id': 'test_device'
                                       })
    token = login_response.json['token']
    headers = {'Authorization': f'Bearer {token}'}

    # Test con dati invalidi
    invalid_data = {'document_type': 'invalid_type', 'document_number': ''}
    response = await client.post('/auth/kyc/submit',
                                 json=invalid_data,
                                 headers=headers)
    assert response.status_code == 400
    assert 'error' in response.json['status']
