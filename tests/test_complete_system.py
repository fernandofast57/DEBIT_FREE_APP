
import pytest
from app import create_app, db
from app.models import User, MoneyAccount, GoldAccount
from decimal import Decimal
from config import TestConfig

@pytest.fixture
async def app():
    """Creates a test application instance."""
    app = create_app(TestConfig)
    
    async with app.app_context():
        await db.create_all()
        
        # Create test user and accounts
        user = User(
            email='test@example.com',
            blockchain_address='0x123...'
        )
        db.session.add(user)
        await db.session.flush()
        
        money_account = MoneyAccount(
            user_id=user.id,
            balance=Decimal('1000.00')
        )
        gold_account = GoldAccount(
            user_id=user.id,
            balance=Decimal('0')
        )
        db.session.add_all([money_account, gold_account])
        await db.session.commit()
        
        yield app
        
        await db.session.remove()
        await db.drop_all()

@pytest.fixture
async def client(app):
    """Creates a test client."""
    return app.test_client()

@pytest.mark.asyncio
async def test_system_health(client):
    """Base test to verify system health."""
    response = await client.get('/api/health')
    assert response.status_code == 200
    assert b'ok' in response.data

@pytest.mark.asyncio
async def test_user_balance(client):
    """Test user account balance retrieval."""
    response = await client.get('/api/v1/accounts/balance/1')
    assert response.status_code == 200
    data = await response.get_json()
    assert 'money_balance' in data
    assert 'gold_balance' in data

@pytest.mark.asyncio
async def test_transformation_flow(client):
    """Test complete transformation flow."""
    response = await client.post('/api/v1/transformations/transform',
        json={
            'user_id': 1,
            'euro_amount': 500.00
        })
    
    assert response.status_code == 200
    data = await response.get_json()
    assert data['status'] == 'success'
    assert 'transaction_id' in data
