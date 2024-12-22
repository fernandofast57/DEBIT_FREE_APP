
import pytest
from decimal import Decimal
from app import create_app, db
from app.models import User, MoneyAccount, GoldAccount, NobleRank
from config import TestConfig

@pytest.fixture
def app():
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        
        # Setup test user with noble rank
        user = User(email='test@test.com')
        noble_rank = NobleRank(rank_name='Bronze', min_investment=Decimal('0'))
        db.session.add(noble_rank)
        db.session.add(user)
        db.session.flush()

        user.noble_rank_id = noble_rank.id
        
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
    """Test API trasformazione con sistema nobiliare"""
    response = test_client.post('/api/v1/transformations/transform',
        json={
            'user_id': 1,
            'fixing_price': 1800.50,
            'batch_id': 'BATCH001'
        })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'noble_bonus' in data

def test_batch_processing(test_client):
    """Test elaborazione batch"""
    response = test_client.post('/api/v1/transfers/batch',
        json={
            'batch_id': 'BATCH001',
            'transactions': [
                {
                    'user_id': 1,
                    'amount': 500.00
                }
            ]
        })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['batch_status'] == 'processed'
