import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import patch, MagicMock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import db
from app.models.models import (
    User, MoneyAccount, GoldAccount, Transaction,
    GoldTransformation, NobleRank, NobleRelation,
    BonusTransaction, GoldAllocation
)
from app.services.gold.weekly_distribution import WeeklyGoldDistribution
from app.utils.monitoring.performance import performance_monitor
from app.core.exceptions import DistributionError

pytestmark = [pytest.mark.asyncio, pytest.mark.gold]

@pytest.fixture
async def noble_ranks(test_db):
    """Setup noble ranks for testing"""
    async with db.async_session() as session:
        async with session.begin():
            ranks = [
                NobleRank(
                    rank_name='Knight',
                    bonus_rate=Decimal('0.007'),
                    min_investment=Decimal('1000.00'),
                    level=1
                ),
                NobleRank(
                    rank_name='Baron',
                    bonus_rate=Decimal('0.005'),
                    min_investment=Decimal('5000.00'),
                    level=2
                ),
                NobleRank(
                    rank_name='Count',
                    bonus_rate=Decimal('0.005'),
                    min_investment=Decimal('10000.00'),
                    level=3
                )
            ]
            for rank in ranks:
                session.add(rank)
            return ranks

@pytest.fixture
async def test_user_with_noble_rank(test_db, noble_ranks):
    """Create test user with noble rank"""
    async with db.async_session() as session:
        async with session.begin():
            user = User(
                username='testuser',
                email='test@example.com',
                money_account=MoneyAccount(balance=Decimal('1000.00')),
                gold_account=GoldAccount(balance=Decimal('0.00'))
            )
            session.add(user)
            await session.flush()

            # Assign noble rank
            noble_relation = NobleRelation(
                user_id=user.id,
                noble_rank_id=noble_ranks[0].id,  # Knight rank
                status='active'
            )
            session.add(noble_relation)
            await session.flush()
            return user

class TestWeeklyDistribution:
    async def test_complete_distribution_flow_with_noble_ranks(
        self, 
        test_user_with_noble_rank, 
        distribution_service
    ):
        """Test distribution including noble ranks and performance monitoring"""
        fixing_price = Decimal('1800.00')
        expected_gold_amount = Decimal('0.5185')  # (1000 * (1 - 0.067)) / 1800

        # Execute distribution with performance monitoring
        with patch('app.services.gold.weekly_distribution.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 15, 30)
            mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 15, 30)

            start_time = datetime.now()
            result = await distribution_service.process_distribution(fixing_price)
            execution_time = (datetime.now() - start_time).total_seconds()

        # Verify performance metrics
        performance_metrics = performance_monitor.get_metrics()
        assert 'distribution_time' in performance_metrics
        assert execution_time < 2.0  # Performance threshold

        # Verify distribution results
        assert result['status'] == 'success'
        assert result['total_euro'] == Decimal('1000.00')
        assert result['total_gold'] == expected_gold_amount

        # Verify database state
        async with db.async_session() as session:
            # Check user accounts
            user = await session.get(User, test_user_with_noble_rank.id)
            assert user.money_account.balance == Decimal('0')
            assert user.gold_account.balance == expected_gold_amount

            # Check noble rank bonus
            bonus_txs = await session.execute(
                select(BonusTransaction).filter_by(user_id=user.id)
            )
            bonus_tx = bonus_txs.scalar_one_or_none()
            assert bonus_tx is not None
            assert bonus_tx.amount > Decimal('0')

            # Check gold allocation
            allocation = await session.execute(
                select(GoldAllocation).filter_by(user_id=user.id)
            )
            allocation = allocation.scalar_one_or_none()
            assert allocation is not None
            assert allocation.grams_allocated == expected_gold_amount

    async def test_multi_level_affiliate_distribution(
        self, 
        test_db, 
        noble_ranks, 
        distribution_service
    ):
        """Test distribution with multi-level affiliates"""
        async with db.async_session() as session:
            async with session.begin():
                # Create affiliate chain: level3 <- level2 <- level1 <- user
                level3 = User(
                    username='level3',
                    email='level3@test.com',
                    money_account=MoneyAccount(balance=Decimal('0.00')),
                    gold_account=GoldAccount(balance=Decimal('0.00'))
                )
                session.add(level3)
                await session.flush()

                level2 = User(
                    username='level2',
                    email='level2@test.com',
                    referrer_id=level3.id,
                    money_account=MoneyAccount(balance=Decimal('0.00')),
                    gold_account=GoldAccount(balance=Decimal('0.00'))
                )
                session.add(level2)
                await session.flush()

                level1 = User(
                    username='level1',
                    email='level1@test.com',
                    referrer_id=level2.id,
                    money_account=MoneyAccount(balance=Decimal('0.00')),
                    gold_account=GoldAccount(balance=Decimal('0.00'))
                )
                session.add(level1)
                await session.flush()

                user = User(
                    username='user',
                    email='user@test.com',
                    referrer_id=level1.id,
                    money_account=MoneyAccount(balance=Decimal('1000.00')),
                    gold_account=GoldAccount(balance=Decimal('0.00'))
                )
                session.add(user)
                await session.flush()

        # Execute distribution
        result = await distribution_service.process_distribution(Decimal('1800.00'))
        assert result['status'] == 'success'

        # Verify affiliate bonuses
        async with db.async_session() as session:
            for level_user in [level1, level2, level3]:
                bonus_txs = await session.execute(
                    select(BonusTransaction).filter_by(user_id=level_user.id)
                )
                bonus_tx = bonus_txs.scalar_one()
                assert bonus_tx is not None
                assert bonus_tx.amount > Decimal('0')

    @pytest.mark.parametrize(
        "fixing_price,balance,expected_error",
        [
            (Decimal('-1800.00'), Decimal('1000.00'), "Invalid fixing price"),
            (Decimal('0.00'), Decimal('1000.00'), "Invalid fixing price"),
            (Decimal('1800.00'), Decimal('-1000.00'), "Invalid balance"),
        ]
    )
    async def test_distribution_validation(
        self,
        test_db,
        distribution_service,
        fixing_price,
        balance,
        expected_error
    ):
        """Test validation with various invalid inputs"""
        async with db.async_session() as session:
            async with session.begin():
                user = User(
                    username='testuser',
                    email='test@example.com',
                    money_account=MoneyAccount(balance=balance),
                    gold_account=GoldAccount(balance=Decimal('0.00'))
                )
                session.add(user)

        with pytest.raises(ValueError, match=expected_error):
            await distribution_service.process_distribution(fixing_price)

    async def test_performance_under_load(
        self,
        test_db,
        noble_ranks,
        distribution_service
    ):
        """Test performance with a large number of users"""
        user_count = 100
        async with db.async_session() as session:
            async with session.begin():
                for i in range(user_count):
                    user = User(
                        username=f'testuser{i}',
                        email=f'test{i}@example.com',
                        money_account=MoneyAccount(balance=Decimal('1000.00')),
                        gold_account=GoldAccount(balance=Decimal('0.00'))
                    )
                    session.add(user)
                    if i % 10 == 0:  # Every 10th user gets a noble rank
                        noble_relation = NobleRelation(
                            user_id=user.id,
                            noble_rank_id=noble_ranks[0].id,
                            status='active'
                        )
                        session.add(noble_relation)

        start_time = datetime.now()
        result = await distribution_service.process_distribution(Decimal('1800.00'))
        execution_time = (datetime.now() - start_time).total_seconds()

        assert result['status'] == 'success'
        assert result['users_processed'] == user_count
        assert execution_time < 10.0  # Performance threshold for 100 users

        # Verify performance metrics
        metrics = performance_monitor.get_metrics()
        assert metrics['distribution_time']['average'] < 0.1  # Average time per user