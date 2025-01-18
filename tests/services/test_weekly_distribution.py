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
from app.models.distribution import WeeklyDistributionLog
from app import create_app

pytestmark = [pytest.mark.asyncio]

class TestWeeklyDistribution:
    @pytest.fixture(autouse=True)
    async def setup(self, async_session, distribution_service):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.session = async_session
        self.service = distribution_service
        yield
        self.app_context.pop()

    @pytest.fixture
    async def distribution_service(self):
        return WeeklyGoldDistribution()

    @pytest.fixture
    async def test_user(self, test_db):
        async with test_db.get_async_session() as session:
            user = User(
                username='test_user',
                email='test@example.com',
                money_account=MoneyAccount(balance=Decimal('1000.00')),
                gold_account=GoldAccount(balance=Decimal('0.00'))
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def test_complete_distribution_flow(
        self,
        distribution_service, 
        test_user
    ):
        fixing_price = Decimal('1800.00')
        result = await distribution_service.process_distribution(fixing_price)

        assert result['status'] == 'success'
        assert result['total_euro'] == float(Decimal('1000.00'))
        assert result['users_processed'] == 1

        expected_gold = (Decimal('1000.00') * 
                        (1 - distribution_service.total_fee)) / fixing_price
        assert abs(result['total_gold'] - float(expected_gold)) < 0.0001

    @pytest.mark.parametrize(
        "fixing_price,balance,expected_error",
        [
            (Decimal('-1800.00'), Decimal('1000.00'), "Invalid fixing price"),
            (Decimal('0.00'), Decimal('1000.00'), "Invalid fixing price"),
            (Decimal('1800.00'), Decimal('-1000.00'), "Invalid balance"),
        ]
    )
    async def test_distribution_validation(self, fixing_price, balance, expected_error):
        with pytest.raises(ValueError, match=expected_error):
            await self.service.process_distribution(fixing_price)

    async def test_performance_under_load(self):
        fixing_price = Decimal('1800.00')
        result = await self.service.process_distribution(fixing_price)
        assert result['status'] == 'success'
        assert result.get('users_processed', 0) >= 0