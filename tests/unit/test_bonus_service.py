
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch
from app.services.bonus_distribution_service import BonusDistributionService
from app.models.models import User, MoneyAccount, GoldAccount
from app.database import db

@pytest.fixture
def bonus_service():
    return BonusDistributionService()

@pytest.fixture
async def mock_user():
    user = User(
        id=1,
        username="test_user",
        email="test@example.com"
    )
    user.money_account = MoneyAccount(balance=Decimal('1000.00'))
    user.gold_account = GoldAccount(balance=Decimal('10.00'))
    return user

@pytest.mark.asyncio
async def test_calculate_weekly_bonus(bonus_service, mock_user):
    transactions = [
        {'amount': Decimal('100.00'), 'timestamp': 1645564800},
        {'amount': Decimal('200.00'), 'timestamp': 1645564800}
    ]
    bonus = await bonus_service.calculate_weekly_bonus(mock_user, transactions)
    assert isinstance(bonus, Decimal)
    assert bonus > 0

@pytest.mark.asyncio
async def test_calculate_bonus_percentage(bonus_service, mock_user):
    gold_balance = Decimal('10.00')
    percentage = await bonus_service.calculate_bonus_percentage(mock_user, gold_balance)
    assert isinstance(percentage, Decimal)
    assert 0 <= percentage <= 100

@pytest.mark.asyncio
async def test_distribute_bonus(bonus_service, mock_user):
    with patch.object(db.session, 'commit'):
        bonus_amount = Decimal('50.00')
        result = await bonus_service.distribute_bonus(mock_user, bonus_amount)
        assert result['status'] == 'success'
        assert mock_user.money_account.balance == Decimal('1050.00')

@pytest.mark.asyncio
async def test_zero_bonus_distribution(bonus_service, mock_user):
    with patch.object(db.session, 'commit'):
        bonus_amount = Decimal('0.00')
        result = await bonus_service.distribute_bonus(mock_user, bonus_amount)
        assert result['status'] == 'skipped'
        assert mock_user.money_account.balance == Decimal('1000.00')

@pytest.mark.asyncio
async def test_negative_bonus_validation(bonus_service, mock_user):
    with pytest.raises(ValueError):
        await bonus_service.distribute_bonus(mock_user, Decimal('-10.00'))

@pytest.mark.asyncio
async def test_bonus_calculation_no_transactions(bonus_service, mock_user):
    transactions = []
    bonus = await bonus_service.calculate_weekly_bonus(mock_user, transactions)
    assert bonus == Decimal('0.00')

@pytest.mark.asyncio
async def test_bonus_calculation_with_rank(bonus_service, mock_user):
    mock_user.noble_rank = 2
    transactions = [{'amount': Decimal('100.00'), 'timestamp': 1645564800}]
    bonus = await bonus_service.calculate_weekly_bonus(mock_user, transactions)
    assert bonus > 0
    assert bonus > Decimal('0.00')

@pytest.mark.asyncio
async def test_bonus_distribution_with_error(bonus_service, mock_user):
    with patch.object(db.session, 'commit', side_effect=Exception('Database error')):
        result = await bonus_service.distribute_bonus(mock_user, Decimal('50.00'))
        assert result['status'] == 'error'
        assert 'Database error' in result['message']

@pytest.mark.asyncio
async def test_bonus_percentage_limits(bonus_service, mock_user):
    max_gold = Decimal('1000.00')
    percentage = await bonus_service.calculate_bonus_percentage(mock_user, max_gold)
    assert percentage <= Decimal('100.00')

@pytest.mark.asyncio
async def test_bonus_distribution_notification(bonus_service, mock_user):
    with patch('app.services.notification_service.NotificationService.send_notification') as mock_notify:
        result = await bonus_service.distribute_bonus(mock_user, Decimal('50.00'))
        assert result['status'] == 'success'
        mock_notify.assert_called_once()
