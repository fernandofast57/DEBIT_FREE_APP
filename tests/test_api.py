
import pytest
from decimal import Decimal
from app import create_app
from app.models.models import User, MoneyAccount, GoldAccount
from app.models.noble_system import NobleRank
from app.utils.database.connection import db

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        noble_rank = NobleRank(rank_name='Bronze', min_investment=Decimal('0'), bonus_rate=Decimal('0.001'))
        db.session.add(noble_rank)
        
        user = User(
            email='test@test.com',
            blockchain_address='0x123test',
            username='test_user'
        )
        user.noble_rank_id = 1
        db.session.add(user)
        
        money_account = MoneyAccount(user_id=1, balance=Decimal('1000.00'))
        gold_account = GoldAccount(user_id=1, balance=Decimal('0'))
        db.session.add_all([money_account, gold_account])
        db.session.commit()
        
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_noble_transformation_api(client):
    """Test noble system transformation with bonus"""
    response = client.post('/api/v1/transformations/transform',
        json={
            'user_id': 1,
            'fixing_price': 1800.50,
            'batch_id': 'BATCH001'
        })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'noble_bonus' in data
    assert float(data['noble_bonus']) > 0

def test_batch_processing(client):
    """Test batch transaction processing"""
    response = client.post('/api/v1/transfers/batch',
        json={
            'batch_id': 'BATCH001',
            'transactions': [
                {
                    'user_id': 1,
                    'amount': 500.00,
                    'type': 'GOLD_PURCHASE'
                }
            ]
        })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['batch_status'] == 'processed'

def test_noble_status_api(client):
    """Test noble rank status endpoint"""
    response = client.get('/api/v1/noble/rank')
    assert response.status_code == 200
    data = response.get_json()
    assert 'current_rank' in data
    assert data['current_rank'] == 'Bronze'
