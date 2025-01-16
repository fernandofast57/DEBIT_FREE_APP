
import pytest
from decimal import Decimal
from datetime import datetime
from app.services.gold.weekly_distribution import WeeklyGoldDistribution
from app.services.gold.distribution_validator import DistributionValidator
from app.models.distribution import WeeklyDistributionLog, DistributionSnapshot

@pytest.mark.asyncio
class TestWeeklyGoldDistribution:
    async def test_distribution_process(self, test_db):
        distribution = WeeklyGoldDistribution()
        fixing_price = Decimal('1800.00')
        
        result = await distribution.process_distribution(fixing_price)
        
        assert result['status'] == 'success'
        assert result['total_euro'] >= 0
        assert result['total_gold'] >= 0
        assert result['users_processed'] >= 0

    async def test_backup_restore(self, test_db):
        distribution = WeeklyGoldDistribution()
        
        # Create initial snapshot
        snapshot_id = await distribution.backup.create_snapshot()
        assert snapshot_id > 0
        
        # Modify some data
        async with db.session() as session:
            await session.execute(
                "UPDATE money_accounts SET balance = balance + 100 WHERE id = 1"
            )
            await session.commit()
            
        # Restore snapshot
        await distribution.backup.restore_latest_snapshot()
        
        # Verify restoration
        async with db.session() as session:
            result = await session.execute(
                "SELECT balance FROM money_accounts WHERE id = 1"
            )
            balance = result.scalar()
            assert balance == Decimal('100')

    async def test_validation(self):
        validator = DistributionValidator()
        
        # Test fixing price validation
        assert await validator.validate_fixing_price(Decimal('1800.00')) is True
        assert await validator.validate_fixing_price(Decimal('0')) is False
        assert await validator.validate_fixing_price(Decimal('-100')) is False
