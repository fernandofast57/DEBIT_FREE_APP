
import pytest
from decimal import Decimal
from app.models.models import User, MoneyAccount, GoldAccount
from app.services.transformation_service import TransformationService
from app.config.settings import CLIENT_SHARE, NETWORK_SHARE

@pytest.fixture
def setup_accounts(app):
    with app.app_context():
        user = User(username="test_user", email="test@example.com")
        money_account = MoneyAccount(balance=Decimal('1000.00'))
        gold_account = GoldAccount(balance=Decimal('0.00'))
        user.money_account = money_account
        user.gold_account = gold_account
        return user, money_account, gold_account

def test_valid_transformation(app, setup_accounts):
    user, money_account, gold_account = setup_accounts
    service = TransformationService()
    
    amount = Decimal('100.00')
    result = service.transform_money_to_gold(user.id, amount)
    
    assert result.success is True
    assert money_account.balance == Decimal('900.00')
    assert gold_account.balance == amount * CLIENT_SHARE

def test_insufficient_funds(app, setup_accounts):
    user, money_account, gold_account = setup_accounts
    service = TransformationService()
    
    amount = Decimal('2000.00')
    result = service.transform_money_to_gold(user.id, amount)
    
    assert result.success is False
    assert money_account.balance == Decimal('1000.00')
    assert gold_account.balance == Decimal('0.00')
