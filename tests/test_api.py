
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
    with app.app_context():
        db.create_all()
        
        # Setup test user with accounts
        noble_rank = NobleRank(rank_name='Silver', min_investment=Decimal('5000.00'))
        db.session.add(noble_rank)
        
        user = User(email='test@example.com', noble_rank_id=noble_rank.id)
        db.session.add(user)
        
        money_account = MoneyAccount(user_id=user.id, balance=Decimal('1000.00'))
        gold_account = GoldAccount(user_id=user.id, balance=Decimal('0'))
        
        db.session.add(money_account)
        db.session.add(gold_account)
        db.session.commit()

        # Test transformation request
        response = client.post('/api/v1/transform', json={
            'user_id': user.id,
            'fixing_price': '50.00'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'verified'
        
        db.session.remove()
        db.drop_all()
