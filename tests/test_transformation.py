
import pytest
from decimal import Decimal
from app import create_app
from app.models.models import User, MoneyAccount, GoldAccount, GoldTransformation
from tests.helpers import get_test_auth_headers
import concurrent.futures
from app.database import db

@pytest.fixture
def app():
    """Create a Flask application object."""
    from config import TestConfig
    
    app = create_app(TestConfig())
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-key'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create a test user with required accounts"""
    user = User(username="testuser", email="test@example.com")
    user.money_account = MoneyAccount(balance=Decimal('2000.00'))
    user.gold_account = GoldAccount(balance=Decimal('0.00'))
    db.session.add(user)
    db.session.commit()
    return user

def test_valid_transformation(app, client, test_user):
    """Test valid transformation request with database verification"""
    assert test_user is not None, "No test user found"
    assert test_user.money_account is not None, "User lacks a MoneyAccount"
    assert test_user.gold_account is not None, "User lacks a GoldAccount"
    
    headers = get_test_auth_headers(test_user)
    initial_gold_balance = test_user.gold_account.balance
    initial_money_balance = test_user.money_account.balance
    
    response = client.post('/api/v1/transformations/transform', headers=headers, json={
        "euro_amount": 150.00,
        "fixing_price": 50.00,
        "fee_amount": 5.00,
        "gold_grams": 3.5
    })
    
    assert response.status_code == 200, f"Failed with status {response.status_code}: {response.get_json()}"
    assert "Gold transformed successfully" in response.get_json()["message"]
    
    db.session.refresh(test_user)
    assert test_user.gold_account.balance == initial_gold_balance + Decimal('3.5')
    assert test_user.money_account.balance == initial_money_balance - Decimal('150.00')
    
    transformation = GoldTransformation.query.filter_by(user_id=test_user.id).order_by(GoldTransformation.created_at.desc()).first()
    assert transformation is not None
    assert transformation.euro_amount == Decimal('150.00')
    assert transformation.gold_grams == Decimal('3.5')
