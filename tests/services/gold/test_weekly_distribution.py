import pytest
from decimal import Decimal
from datetime import datetime
from app.database import db
from app.services.gold.weekly_distribution import WeeklyGoldDistribution

pytestmark = [pytest.mark.asyncio, pytest.mark.gold]  # Aggiungiamo entrambi i marker

@pytest.mark.usefixtures("app", "test_db")
class TestWeeklyGoldDistribution:
    # I test rimangono gli stessi

    async def test_distribution_process(self, test_db):
        distribution = WeeklyGoldDistribution()
        fixing_price = Decimal('1800.00')

        result = await distribution.process_distribution(fixing_price)

        assert result['status'] == 'success'
        assert result['total_euro'] >= 0
        assert result['total_gold'] >= 0
        assert result['users_processed'] >= 0
        assert 'total_affiliate_bonus' in result
        assert result['fixing_price'] == float(fixing_price)

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
        restored = await distribution.backup.restore_latest_snapshot()
        assert restored is True

        # Verify restoration
        async with db.session() as session:
            result = await session.execute(
                "SELECT balance FROM money_accounts WHERE id = 1")
            balance = result.scalar()
            assert balance == Decimal('100')

    async def test_validation(self):
        validator = DistributionValidator()

        # Test fixing price validation
        assert await validator.validate_fixing_price(Decimal('1800.00')
                                                     ) is True
        assert await validator.validate_fixing_price(Decimal('0')) is False
        assert await validator.validate_fixing_price(Decimal('-100')) is False

    async def test_affiliate_distribution(self, test_db):
        distribution = WeeklyGoldDistribution()
        user_id = 1
        gold_amount = Decimal('10.00')

        result = await distribution.distribute_affiliate_bonuses(
            user_id, gold_amount)

        assert isinstance(result, dict)
        if result:  # Se ci sono referral
            assert 'level_1' in result
            assert float(result['level_1']) == float(gold_amount *
                                                     Decimal('0.007'))

    async def test_pre_distribution_checks(self, test_db):
        distribution = WeeklyGoldDistribution()

        # Test system checks
        check_result = await distribution.pre_distribution_checks()
        assert isinstance(check_result, bool)

    async def test_error_handling(self, test_db):
        distribution = WeeklyGoldDistribution()

        # Test con prezzo fixing invalido
        result = await distribution.process_distribution(Decimal('-1'))
        assert result['status'] == 'error'
        assert 'error' in result
        assert 'timestamp' in result

    @pytest.mark.parametrize("fixing_price,expected_status",
                             [(Decimal('1800.00'), 'success'),
                              (Decimal('0'), 'error'),
                              (Decimal('-100'), 'error'),
                              (Decimal('100000.01'), 'error')])
    async def test_multiple_scenarios(self, test_db, fixing_price,
                                      expected_status):
        distribution = WeeklyGoldDistribution()
        result = await distribution.process_distribution(fixing_price)
        assert result['status'] == expected_status

    async def test_concurrent_execution(self, test_db):
        distribution = WeeklyGoldDistribution()
        fixing_price = Decimal('1800.00')

        # Esegui due distribuzioni contemporaneamente
        tasks = [
            distribution.process_distribution(fixing_price),
            distribution.process_distribution(fixing_price)
        ]

        import asyncio
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verifica che solo una distribuzione sia andata a buon fine
        success_count = sum(
            1 for r in results
            if isinstance(r, dict) and r['status'] == 'success')
        assert success_count == 1
