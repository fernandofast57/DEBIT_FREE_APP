
import pytest
from decimal import Decimal
from app import create_app
from app.models.models import User, MoneyAccount, GoldAccount, GoldTransformation
from tests.helpers import get_test_auth_headers
from app.database import db

@pytest.fixture(scope='function')
def app():
    from config import TestConfig
    config = TestConfig()
    config.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    app = create_app(config)
    
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
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        user.money_account = MoneyAccount(balance=Decimal('2000.00'))
        user.gold_account = GoldAccount(balance=Decimal('0.00'))
        db.session.add(user)
        db.session.commit()
        return user

def test_valid_transformation(app, client, test_user):
    with app.app_context():
        headers = get_test_auth_headers(test_user)
        initial_gold_balance = test_user.gold_account.balance
        initial_money_balance = test_user.money_account.balance
        
        response = client.post('/api/v1/transformations/transform', 
            headers=headers, 
            json={
                "euro_amount": 150.00,
                "fixing_price": 50.00,
                "fee_amount": 5.00,
                "gold_grams": 3.5
            })
        
        assert response.status_code == 200
        db.session.refresh(test_user)
        assert test_user.gold_account.balance == initial_gold_balance + Decimal('3.5')
        assert test_user.money_account.balance == initial_money_balance - Decimal('150.00')
