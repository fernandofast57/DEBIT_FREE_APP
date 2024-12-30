
import pytest
from decimal import Decimal
from app.models.models import User, MoneyAccount, GoldAccount
from app.services.transformation_service import TransformationService
from app.utils.errors import InsufficientBalanceError

@pytest.fixture
def setup_accounts(app):
    with app.app_context():
        user = User(username="test_user", email="test@example.com")
        money_account = MoneyAccount(balance=Decimal('1000.00'))
        gold_account = GoldAccount(balance=Decimal('0.00'))
        user.money_account = money_account
        user.gold_account = gold_account
        return user, money_account, gold_account

@pytest.mark.asyncio
async def test_valid_transformation(app, setup_accounts):
    user, money_account, gold_account = setup_accounts
    service = TransformationService()
    await service.initialize()
    
    fixing_price = Decimal('50.00')
    result = await service.transform_to_gold(user.id, fixing_price)
    
    assert result['status'] == 'verified'
    assert money_account.balance == Decimal('0.00')
    assert gold_account.balance > Decimal('0.00')

@pytest.mark.asyncio
async def test_insufficient_balance(app, setup_accounts):
    user, money_account, gold_account = setup_accounts
    money_account.balance = Decimal('0.00')
    service = TransformationService()
    await service.initialize()
    
    fixing_price = Decimal('50.00')
    result = await service.transform_to_gold(user.id, fixing_price)
    
    assert result['status'] == 'error'
    assert 'Insufficient balance' in result['message']
    assert money_account.balance == Decimal('0.00')
    assert gold_account.balance == Decimal('0.00')

@pytest.mark.asyncio
async def test_invalid_fixing_price(app, setup_accounts):
    user, money_account, gold_account = setup_accounts
    service = TransformationService()
    await service.initialize()
    
    fixing_price = Decimal('0.00')
    result = await service.validate_transformation(Decimal('1000.00'), fixing_price)
    
    assert result['status'] == 'rejected'
    assert 'Invalid fixing price' in result['message']
