import pytest
from app import create_app

@pytest.mark.asyncio
async def test_index(client):
    """Testare l'endpoint radice per il successo"""
    response = await client.get('/')
    assert response.status_code == 200
    assert response.json == {
        "status": "online",
        "service": "Gold Investment API",
        "version": "1.0"
    }

@pytest.mark.asyncio
async def test_invalid_transformation(client):
    """Trasformazione di prova con input non valido"""
    response = await client.post('/api/v1/transformations/transform', json={
        "euro_amount": -100,  # Invalid amount
        "fixing_price": 50.00
    })
    assert response.status_code == 400  # Validation should fail
    assert 'error' in response.json
