import pytest
from app import create_app
from flask import json
from app.models.models import User, MoneyAccount, GoldAccount
from decimal import Decimal

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers():
    return {'X-User-Id': '123', 'Authorization': 'Bearer test-token'}

@pytest.mark.asyncio
async def test_transformation_endpoint(client, auth_headers):
    response = await client.post('/api/v1/transformation', 
        json={
            'amount': 100.0,
            'fixing_price': 50.0
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'

@pytest.mark.asyncio
async def test_account_balance(client, auth_headers):
    # Setup test user with accounts
    user = User(id=1)
    user.money_account = MoneyAccount(balance=Decimal('1000.00'))
    user.gold_account = GoldAccount(balance=Decimal('0'))

    response = await client.get('/api/v1/account/balance',
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.get_json()
    assert 'money_balance' in data
    assert 'gold_balance' in data

def test_index(client):
    """Test root endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "status" in data

@pytest.mark.asyncio
async def test_invalid_transformation(client, auth_headers):
    response = await client.post('/api/v1/transformation',
        json={
            'amount': -100.0,
            'fixing_price': 50.0
        },
        headers=auth_headers
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data['status'] == 'error'

def test_async_endpoints(client, auth_headers):
    """Test endpoints that require async client"""
    response = client.get('/api/v1/status', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data