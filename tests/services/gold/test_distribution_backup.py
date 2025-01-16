import pytest
from decimal import Decimal
from app.services.gold.distribution_backup import DistributionBackup
from app.database import db

pytestmark = [pytest.mark.asyncio, pytest.mark.gold]

@pytest.mark.usefixtures("app", "test_db")
class TestDistributionBackup:
    # I test rimangono gli stessi

    async def test_create_snapshot(self, test_db):
        backup = DistributionBackup()
        snapshot_id = await backup.create_snapshot()
        assert snapshot_id > 0

    async def test_restore_snapshot(self, test_db):
        backup = DistributionBackup()

        # Create initial state
        async with db.session() as session:
            await session.execute(
                "UPDATE money_accounts SET balance = 100 WHERE id = 1")
            await session.commit()

        # Create snapshot
        snapshot_id = await backup.create_snapshot()

        # Modify state
        async with db.session() as session:
            await session.execute(
                "UPDATE money_accounts SET balance = 200 WHERE id = 1")
            await session.commit()

        # Restore
        restored = await backup.restore_latest_snapshot()
        assert restored is True

        # Verify
        async with db.session() as session:
            result = await session.execute(
                "SELECT balance FROM money_accounts WHERE id = 1")
            balance = result.scalar()
            assert balance == Decimal('100')

    async def test_verify_snapshot_integrity(self, test_db):
        backup = DistributionBackup()
        snapshot_id = await backup.create_snapshot()

        integrity_result = await backup.verify_snapshot_integrity(snapshot_id)
        assert integrity_result is True

    async def test_snapshot_not_found(self, test_db):
        backup = DistributionBackup()
        integrity_result = await backup.verify_snapshot_integrity(999999)
        assert integrity_result is False
