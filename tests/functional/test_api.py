
import pytest
from app import create_app
from flask import json

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers():
    return {'X-User-Id': '123', 'Authorization': 'Bearer test-token'}

def test_transformation_endpoint(client, auth_headers):
    """Test transformation endpoint"""
    response = client.post('/api/v1/transformations/transform',
        json={
            "fixing_price": 50.00,
            "gold_grams": 2.0
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data

def test_account_balance(client, auth_headers):
    """Test account balance endpoint"""
    response = client.get('/api/v1/accounts/balance',
        headers=auth_headers
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "gold_balance" in data or "balance" in data

def test_index(client):
    """Test root endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "status" in data

def test_invalid_transformation(client, auth_headers):
    """Test transformation with invalid input"""
    response = client.post('/api/v1/transformations/transform', 
        json={
            "fixing_price": -50.00,
            "gold_grams": 0
        },
        headers=auth_headers
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'errors' in data

def test_async_endpoints(client, auth_headers):
    """Test endpoints that require async client"""
    response = client.get('/api/v1/status', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data
