import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import patch, MagicMock
from app.database import db
from app.models.models import User, MoneyAccount, GoldAccount
from app.models.distribution import WeeklyDistributionLog
from app.services.gold.weekly_distribution import WeeklyGoldDistribution

pytestmark = [pytest.mark.asyncio, pytest.mark.gold]

@pytest.fixture
async def test_user(test_db):
    async with db.session() as session:
        user = User(username='testuser', email='test@example.com')
        money_account = MoneyAccount(balance=Decimal('1000.00'))
        gold_account = GoldAccount(balance=Decimal('0.00'))
        user.money_account = money_account
        user.gold_account = gold_account
        session.add(user)
        await session.commit()
        return user

@pytest.fixture
async def distribution_service():
    """Fixture per il servizio di distribuzione"""
    service = WeeklyGoldDistribution()
    return service

@pytest.mark.asyncio
async def test_distribution_process(test_user, distribution_service):
    """Test del processo di distribuzione con gestione asincrona appropriata"""
    fixing_price = Decimal('1800.00')

    # Mock della data per permettere la distribuzione
    with patch('app.services.gold.weekly_distribution.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2024, 1, 1, 15, 30)
        mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 15, 30)

        # Esegui la distribuzione
        result = await distribution_service.process_distribution(fixing_price)

        # Verifica il risultato
        assert result['status'] == 'success'
        assert Decimal(str(result['total_euro'])) == Decimal('1000.00')
        assert Decimal(str(result['total_gold'])) > Decimal('0')
        assert result['users_processed'] == 1

        # Verifica lo stato dell'utente dopo la distribuzione
        async with db.session() as session:
            await session.refresh(test_user)
            assert test_user.money_account.balance == Decimal('0')
            assert test_user.gold_account.balance > Decimal('0')

@pytest.mark.usefixtures("app", "test_db")
class TestWeeklyGoldDistribution:
    async def test_backup_restore(self, test_db, test_user):
        distribution = WeeklyGoldDistribution()
        
        # Create initial snapshot
        snapshot_id = await distribution.backup.create_snapshot()
        assert snapshot_id is not None

        # Modify data
        async with db.session() as session:
            await session.execute(
                "UPDATE money_accounts SET balance = balance + 100 WHERE user_id = :user_id",
                {'user_id': test_user.id}
            )
            await session.commit()

        # Restore snapshot
        restored = await distribution.backup.restore_latest_snapshot()
        assert restored is True

    async def test_validation(self, test_db):
        distribution = WeeklyGoldDistribution()
        fixing_price = Decimal('1800.00')
        
        with patch('app.services.gold.weekly_distribution.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 15, 30)
            is_valid = await distribution.validator.validate_fixing_price(fixing_price)
            assert is_valid is True

    async def test_affiliate_distribution(self, test_db, test_user):
        distribution = WeeklyGoldDistribution()
        gold_amount = Decimal('10.00')

        result = await distribution.distribute_affiliate_bonuses(test_user.id, gold_amount)
        assert isinstance(result, dict)

    async def test_pre_distribution_checks(self, test_db):
        distribution = WeeklyGoldDistribution()
        
        with patch('app.services.gold.weekly_distribution.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 15, 30)
            result = await distribution.pre_distribution_checks()
            assert result is True

    async def test_error_handling(self, test_db):
        distribution = WeeklyGoldDistribution()
        result = await distribution.process_distribution(Decimal('-1'))
        assert result['status'] == 'error'
        assert 'error' in result

    @pytest.mark.parametrize("fixing_price,expected_status", [
        (Decimal('1800.00'), 'success'),
        (Decimal('0'), 'error'),
        (Decimal('-100'), 'error'),
        (Decimal('100000.01'), 'error')
    ])
    async def test_multiple_scenarios(self, test_db, test_user, fixing_price, expected_status):
        distribution = WeeklyGoldDistribution()
        
        with patch('app.services.gold.weekly_distribution.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 15, 30)
            result = await distribution.process_distribution(fixing_price)
            assert result['status'] == expected_status

    async def test_concurrent_execution(self, test_db, test_user):
        distribution = WeeklyGoldDistribution()
        fixing_price = Decimal('1800.00')

        import asyncio
        tasks = [
            distribution.process_distribution(fixing_price),
            distribution.process_distribution(fixing_price)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        success_count = sum(1 for r in results 
                          if isinstance(r, dict) and r['status'] == 'success')
        assert success_count == 1