
import pytest
from decimal import Decimal
from app.models.models import User, MoneyAccount, GoldAccount, GoldTransformation
from app.services.transformation_service import TransformationService

@pytest.mark.asyncio
async def test_gold_transformation(app, client):
    """Test gold transformation process"""
    async with app.app_context():
        user = User(
            username='test_transform',
            email='transform@test.com',
            password_hash='test_hash'
        )
        money_account = MoneyAccount(balance=Decimal('1000.00'))
        gold_account = GoldAccount(balance=Decimal('0'))
        
        service = TransformationService()
        result = await service.validate_transformation(
            euro_amount=Decimal('1000.00'),
            fixing_price=Decimal('50.00')
        )
        assert result['status'] == 'verified'

@pytest.mark.asyncio
async def test_minimum_transformation_amount(app, client):
    """Test minimum transformation amount validation"""
    service = TransformationService()
    result = await service.validate_transformation(
        euro_amount=Decimal('50.00'),
        fixing_price=Decimal('50.00')
    )
    assert result['status'] == 'rejected'
