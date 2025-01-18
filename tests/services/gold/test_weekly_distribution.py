import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import patch, MagicMock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import db
from app.models.models import User, MoneyAccount, GoldAccount, Transaction
from app.services.gold.weekly_distribution import WeeklyGoldDistribution
from app.core.exceptions import DistributionError

pytestmark = [pytest.mark.asyncio, pytest.mark.gold]


@pytest.fixture
async def test_db():
    """Setup and teardown test database"""
    async with db.engine.begin() as conn:
        await conn.run_sync(db.Base.metadata.create_all)
    yield db
    async with db.engine.begin() as conn:
        await conn.run_sync(db.Base.metadata.drop_all)


@pytest.fixture
async def test_user(test_db):
    """Create test user with accounts"""
    async with db.async_session() as session:
        async with session.begin():
            user = User(username='testuser',
                        email='test@example.com',
                        money_account=MoneyAccount(balance=Decimal('1000.00')),
                        gold_account=GoldAccount(balance=Decimal('0.00')))
            session.add(user)
            await session.flush()
            await session.refresh(user)
            return user


@pytest.fixture
async def mock_blockchain_service():
    service = MagicMock()

    # Setup async mock for blockchain service
    async def async_record_transaction(*args, **kwargs):
        return {'status': 'success', 'transaction_hash': '0x123abc'}

    service.record_gold_transaction = MagicMock(
        side_effect=async_record_transaction)
    return service


@pytest.fixture
def distribution_service(mock_blockchain_service):
    return WeeklyGoldDistribution(blockchain_service=mock_blockchain_service,
                                  notification_service=MagicMock())


class TestWeeklyDistribution:

    async def test_complete_distribution_flow(self, test_user,
                                              distribution_service):
        """Test the complete distribution flow including blockchain validation"""
        fixing_price = Decimal('1800.00')
        expected_gold_amount = Decimal('0.5185')  # (1000 * (1 - 0.067)) / 1800

        # Execute distribution
        with patch('app.services.gold.weekly_distribution.datetime'
                   ) as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 15, 30)
            mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 15, 30)

            result = await distribution_service.process_distribution(
                fixing_price)

        # Verify result structure
        assert result['status'] == 'success'
        assert result['total_euro'] == Decimal('1000.00')
        assert result['total_gold'] == expected_gold_amount
        assert result['users_processed'] == 1

        # Verify database state
        async with db.async_session() as session:
            async with session.begin():
                user = await session.get(User, test_user.id)
                assert user.money_account.balance == Decimal('0')
                assert user.gold_account.balance == expected_gold_amount

                # Verify transaction record
                stmt = select(Transaction).filter_by(user_id=user.id)
                result = await session.execute(stmt)
                transaction = result.scalar_one()

                assert transaction is not None
                assert transaction.blockchain_tx_hash == '0x123abc'
                assert transaction.euro_amount == Decimal('1000.00')
                assert transaction.gold_amount == expected_gold_amount
                assert transaction.fixing_price == fixing_price

    async def test_distribution_validation(self, distribution_service):
        """Test input validation for distribution process"""
        invalid_cases = [(Decimal('-1800.00'), "Invalid fixing price"),
                         (Decimal('0.00'), "Invalid fixing price"),
                         (None, "Fixing price required")]

        for price, expected_error in invalid_cases:
            with pytest.raises(ValueError, match=expected_error):
                await distribution_service.process_distribution(price)

    async def test_distribution_failure_handling(self, test_user,
                                                 distribution_service):
        """Test handling of failures during distribution"""
        fixing_price = Decimal('1800.00')

        # Simulate blockchain failure
        async def failed_blockchain_transaction(*args, **kwargs):
            return {'status': 'error', 'error': 'Blockchain error'}
        distribution_service.blockchain_service.record_gold_transaction = \
            MagicMock(side_effect=failed_blockchain_transaction)

        with pytest.raises(DistributionError) as exc_info:
            await distribution_service.process_distribution(fixing_price)

        assert "Blockchain transaction failed" in str(exc_info.value)

        # Verify state remained unchanged
        async with db.async_session() as session:
            user = await session.get(User, test_user.id)
            assert user.money_account.balance == Decimal('1000.00')
            assert user.gold_account.balance == Decimal('0.00')

    @pytest.mark.parametrize("user_count", [1, 5, 10])
    async def test_distribution_performance(self, test_db, user_count,
                                            distribution_service):
        """Test distribution performance with different user counts"""
        # Create test users
        async with db.async_session() as session:
            async with session.begin():
                for i in range(user_count):
                    user = User(
                        username=f'testuser{i}',
                        email=f'test{i}@example.com',
                        money_account=MoneyAccount(balance=Decimal('1000.00')),
                        gold_account=GoldAccount(balance=Decimal('0.00')))
                    session.add(user)

        start_time = datetime.now()
        result = await distribution_service.process_distribution(
            Decimal('1800.00'))
        execution_time = (datetime.now() - start_time).total_seconds()

        assert result['status'] == 'success'
        assert result['users_processed'] == user_count
        assert execution_time < 2.0  # Performance threshold

        # Verify all users were processed correctly
        async with db.async_session() as session:
            stmt = select(User)
            result = await session.execute(stmt)
            users = result.scalars().all()

            assert len(users) == user_count
            for user in users:
                assert user.money_account.balance == Decimal('0')
                assert user.gold_account.balance > Decimal('0')
