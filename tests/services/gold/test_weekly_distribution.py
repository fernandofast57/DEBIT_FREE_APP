import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import patch, MagicMock
from app.database import db
from app.models.models import User, MoneyAccount, GoldAccount, Transaction
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
def distribution_service():
    return WeeklyGoldDistribution()

@pytest.fixture
def mock_blockchain_service():
    return MagicMock()

@pytest.mark.asyncio
class TestWeeklyDistribution:
    async def test_complete_distribution_flow(self, test_user, distribution_service, mock_blockchain_service):
        """Test the complete distribution flow including blockchain validation"""
        fixing_price = Decimal('1800.00')

        # Mock blockchain service response
        mock_blockchain_service.record_gold_transaction.return_value = {
            'status': 'success',
            'transaction_hash': '0x123abc'
        }

        # Execute distribution
        with patch('app.services.gold.weekly_distribution.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 15, 30)
            mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 15, 30)

            result = await distribution_service.process_distribution(fixing_price)

        # Verify result structure
        assert result['status'] == 'success'
        assert 'total_euro' in result
        assert 'total_gold' in result
        assert 'users_processed' in result

        # Verify database state
        async with db.session() as session:
            user = await session.query(User).filter_by(id=test_user.id).first()
            assert user.money_account.balance == Decimal('0')
            assert user.gold_account.balance > Decimal('0')

            # Verify transaction record
            transaction = await session.query(Transaction).filter_by(user_id=user.id).first()
            assert transaction is not None
            assert transaction.blockchain_tx_hash == '0x123abc'

        # Verify blockchain interaction
        assert mock_blockchain_service.record_gold_transaction.called

    async def test_distribution_validation(self, distribution_service):
        """Test input validation for distribution process"""
        invalid_cases = [
            (Decimal('-1800.00'), "Invalid fixing price"),
            (Decimal('0.00'), "Invalid fixing price"),
            (None, "Fixing price required")
        ]

        for price, expected_error in invalid_cases:
            with pytest.raises(ValueError, match=expected_error):
                await distribution_service.process_distribution(price)

    async def test_distribution_backup_restore(self, test_user, distribution_service):
        """Test backup and restore functionality during distribution"""
        fixing_price = Decimal('1800.00')

        # Create initial snapshot
        snapshot_id = await distribution_service.backup.create_snapshot()
        assert snapshot_id is not None

        # Simulate failed distribution
        with patch.object(distribution_service, 'distribute_gold', side_effect=Exception("Simulated error")):
            result = await distribution_service.process_distribution(fixing_price)
            assert result['status'] == 'error'

        # Verify state is restored
        async with db.session() as session:
            user = await session.query(User).filter_by(id=test_user.id).first()
            assert user.money_account.balance == Decimal('1000.00')
            assert user.gold_account.balance == Decimal('0.00')

    @pytest.mark.parametrize("user_count", [1, 5, 10])
    async def test_distribution_performance(self, test_db, user_count, distribution_service):
        """Test distribution performance with different user counts"""
        # Create test users
        async with db.session() as session:
            for i in range(user_count):
                user = User(
                    username=f'testuser{i}',
                    email=f'test{i}@example.com',
                    money_account=MoneyAccount(balance=Decimal('1000.00')),
                    gold_account=GoldAccount(balance=Decimal('0.00'))
                )
                session.add(user)
            await session.commit()

        # Execute distribution
        result = await distribution_service.process_distribution(Decimal('1800.00'))

        assert result['status'] == 'success'
        assert result['users_processed'] == user_count