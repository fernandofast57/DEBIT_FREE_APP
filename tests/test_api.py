
import pytest
from app import create_app
from app.models import User, MoneyAccount, GoldAccount, NobleRank, db
from decimal import Decimal

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_transform_endpoint(app, client):
    """Test gold transformation according to glossary definition"""
    with app.app_context():
        db.create_all()
        
        noble_rank = NobleRank(rank_name='bronze', bonus_rate=Decimal('0.005'), min_investment=Decimal('1000.00'), level=1)
        db.session.add(noble_rank)
        
        user = User(username='test_user', email='test@example.com')
        db.session.add(user)
        
        money_account = MoneyAccount(balance=Decimal('1000.00'))
        gold_account = GoldAccount(balance=Decimal('0.00'))
        
        user.money_account = money_account
        user.gold_account = gold_account
        
        db.session.commit()

        response = client.post('/api/v1/transformations', json={
            'user_id': user.id,
            'euro_amount': '1000.00',
            'fixing_price': '50.00'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == STATUS_VERIFIED
        assert 'gold_grams' in data
        
        db.session.remove()
        db.drop_all()
