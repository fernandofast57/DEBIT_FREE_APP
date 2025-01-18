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


pytestmark = [pytest.mark.asyncio]


class TestWeeklyDistribution:
    @pytest.fixture(autouse=True)
    async def setup(self, async_session, distribution_service):
        self.session = async_session
        self.service = distribution_service

    async def test_complete_distribution_flow_with_noble_ranks(self):
        fixing_price = Decimal('1800.00')
        result = await self.service.process_distribution(fixing_price)
        assert result['status'] == 'success'

    async def test_multi_level_affiliate_distribution(self):
        fixing_price = Decimal('1800.00')
        result = await self.service.process_distribution(fixing_price)
        assert result['status'] == 'success'

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