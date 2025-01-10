import pytest
from flask import json
from decimal import Decimal
from app.models.models import User, MoneyAccount, GoldAccount
from app.database import db

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
    # Prepara i dati di test
    test_data = {
        "euro_amount": "100.00",
        "fixing_price": "50.00"
    }

    response = client.post('/api/v1/transformations/execute',
                          headers=auth_headers,
                          json=test_data)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "transaction_id" in data
    assert data["status"] == "success"

def test_account_balance(client, auth_headers):
    with client.application.app_context():
        user = User.query.first()
        assert user is not None

        money_account = MoneyAccount.query.filter_by(user_id=user.id).first()
        gold_account = GoldAccount.query.filter_by(user_id=user.id).first()

        assert money_account is not None
        assert gold_account is not None

        response = client.get('/api/v1/accounts/balance',
                            headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "money_balance" in data
        assert "gold_balance" in data

def test_invalid_transformation(client, auth_headers):
    invalid_data = {
        "euro_amount": "-100.00",
        "fixing_price": "0"
    }

    response = client.post('/api/v1/transformations/execute',
                          headers=auth_headers,
                          json=invalid_data)

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data