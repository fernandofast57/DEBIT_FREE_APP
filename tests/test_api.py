
import pytest
from app.models.models import User, MoneyAccount, GoldAccount
from app.services.transformation_service import TransformationService

@pytest.mark.asyncio
async def test_transform_endpoint(client, db):
    # Setup test user
    user = User(email='test@example.com')
    money_account = MoneyAccount(balance=1000.0)
    gold_account = GoldAccount(balance=0.0)
    user.money_account = money_account
    user.gold_account = gold_account
    
    db.session.add(user)
    await db.session.commit()

    response = await client.post('/api/v1/transform', 
        json={'euro_amount': 100.0, 'fixing_price': 1800.50})
    
    assert response.status_code == 200
    data = await response.get_json()
    assert data['status'] == 'success'
