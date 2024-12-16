
import pytest
from decimal import Decimal
from app import create_app, db
from app.models.models import User, MoneyAccount, GoldAccount
from app.models.noble_system import NobleRank, NobleRelation

@pytest.fixture
async def app():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['TESTING'] = True
    
    async with app.app_context():
        await db.create_all()
        
        # Setup test user
        user = User(email='test@test.com')
        db.session.add(user)
        await db.session.flush()

        # Setup accounts
        money_account = MoneyAccount(
            user_id=user.id,
            balance=Decimal('1000.00')
        )
        gold_account = GoldAccount(
            user_id=user.id,
            balance=Decimal('0')
        )
        db.session.add_all([money_account, gold_account])

        # Setup noble ranks
        ranks = [
            NobleRank(title='Nobile', bonus_rate=Decimal('0.007'), level=1),
            NobleRank(title='Visconte', bonus_rate=Decimal('0.005'), level=2),
            NobleRank(title='Conte', bonus_rate=Decimal('0.005'), level=3)
        ]
        db.session.add_all(ranks)
        await db.session.commit()
        
        yield app
        
        await db.session.remove()
        await db.drop_all()

@pytest.fixture
def test_client(app):
    return app.test_client()

@pytest.mark.asyncio
async def test_transformation_api(test_client):
    """Test API trasformazioni"""
    response = await test_client.post('/api/v1/transformations/transform',
        json={
            'user_id': 1,
            'fixing_price': 1800.50
        })
    
    assert response.status_code == 200
    data = await response.get_json()
    assert data['status'] == 'success'

@pytest.mark.asyncio
async def test_transfer_api(test_client):
    """Test API bonifici"""
    response = await test_client.post('/api/v1/transfers/process',
        json={
            'user_id': 1,
            'amount': 500.00
        })
    
    assert response.status_code == 200
    data = await response.get_json()
    assert data['status'] == 'success'
    assert data['transaction']['amount'] == 500.00

@pytest.mark.asyncio
async def test_invalid_inputs(test_client):
    """Test gestione input non validi"""
    response = await test_client.post('/api/v1/transfers/process',
        json={
            'user_id': 1,
            'amount': 'invalid'
        })
    assert response.status_code == 400

    response = await test_client.post('/api/v1/transformations/transform',
        json={
            'user_id': 1,
            'fixing_price': 'invalid'
        })
    assert response.status_code == 400
