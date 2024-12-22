
import pytest
from decimal import Decimal
from app import create_app, db
from app.models import User, MoneyAccount, GoldAccount
from config import TestConfig

@pytest.fixture
def app():
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        
        # Setup test user
        user = User(email='test@test.com')
        db.session.add(user)
        db.session.flush()

        money_account = MoneyAccount(
            user_id=user.id,
            balance=Decimal('1000.00')
        )
        gold_account = GoldAccount(
            user_id=user.id,
            balance=Decimal('0')
        )
        db.session.add_all([money_account, gold_account])
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_client(app):
    return app.test_client()

def test_transformation_api(test_client):
    """Test API trasformazione"""
    response = test_client.post('/api/v1/transformations/transform',
        json={
            'user_id': 1,
            'fixing_price': 1800.50
        })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'

def test_transfer_api(test_client):
    """Test API trasferimenti"""
    response = test_client.post('/api/v1/transfers/process',
        json={
            'user_id': 1,
            'amount': 500.00
        })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['transaction']['amount'] == 500.00
