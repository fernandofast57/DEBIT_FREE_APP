
import pytest
from decimal import Decimal
from app.services.transformation_service import TransformationService
from app.models.models import User, MoneyAccount, GoldAccount

@pytest.mark.asyncio
async def test_transformation_calculates_correct_gold_amount(app):
    with app.app_context():
        service = TransformationService()
        euro_amount = Decimal('100.00')
        fixing_price = Decimal('50.00')
        expected_gold = Decimal('1.90')  # (100 - 5% fee) / 50

        test_user = User(id=1)
        test_user.money_account = MoneyAccount(balance=euro_amount)
        test_user.gold_account = GoldAccount(balance=Decimal('0'))
        
        async def mock_get(user_id):
            return test_user
        User.query.get = mock_get

        result = await service.process_transformation(1, euro_amount, fixing_price)
        
        assert result['status'] == 'success'
        assert Decimal(str(result['gold_grams'])) == expected_gold

@pytest.mark.asyncio
async def test_insufficient_funds_transformation(app):
    with app.app_context():
        service = TransformationService()
        euro_amount = Decimal('1000.00')
        fixing_price = Decimal('50.00')

        test_user = User(id=1)
        test_user.money_account = MoneyAccount(balance=Decimal('100.00'))
        test_user.gold_account = GoldAccount(balance=Decimal('0'))
        
        async def mock_get(user_id):
            return test_user
        User.query.get = mock_get

        result = await service.process_transformation(1, euro_amount, fixing_price)
        assert result['status'] == 'error'
        assert 'insufficient funds' in result['message'].lower()

@pytest.mark.asyncio
async def test_invalid_fixing_price(app):
    with app.app_context():
        service = TransformationService()
        euro_amount = Decimal('100.00')
        fixing_price = Decimal('0')

        test_user = User(id=1)
        test_user.money_account = MoneyAccount(balance=euro_amount)
        test_user.gold_account = GoldAccount(balance=Decimal('0'))
        
        result = await service.process_transformation(1, euro_amount, fixing_price)
        assert result['status'] == 'error'
        assert 'invalid fixing price' in result['message'].lower()
