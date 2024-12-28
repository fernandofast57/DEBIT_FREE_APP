
import pytest
from app import create_app
from flask import json

def test_index(client):
    """Test root endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == {
        "status": "online",
        "service": "Gold Investment API",
        "version": "1.0"
    }

def test_invalid_transformation(client):
    """Test transformation with invalid input"""
    response = client.post('/api/v1/transformations/transform', 
        json={
            "euro_amount": -100,
            "fixing_price": 50.00
        },
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

@pytest.mark.asyncio
async def test_async_endpoints(async_client):
    """Test endpoints that require async client"""
    response = await async_client.get('/api/v1/status')
    assert response.status_code == 200
    data = await response.json()
    assert 'status' in data
