import pytest
from app import create_app
from flask import json
from decimal import Decimal

@pytest.fixture
def auth_headers():
    return {'Authorization': 'Bearer test-token'}

def test_transformation_endpoint(client, auth_headers):
    """Test transformation endpoint"""
    response = client.post('/api/v1/transformations/transform',
        json={
            "euro_amount": 100.00,
            "fixing_price": 50.00
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "gold_grams" in data

def test_account_balance(client, auth_headers):
    """Test account balance endpoint"""
    response = client.get('/api/v1/accounts/balance',
        headers=auth_headers
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "gold_balance" in data
    assert "money_balance" in data

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

def test_async_endpoints(client): #Corrected async test
    """Test endpoints that require async client"""
    response = client.get('/api/v1/status')
    assert response.status_code == 200
    data = response.json()
    assert 'status' in data