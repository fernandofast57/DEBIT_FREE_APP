import pytest
from decimal import Decimal
from app.services.gold.distribution_validator import DistributionValidator
from app.database import db


@pytest.mark.asyncio
class TestDistributionValidator:

    async def test_validate_fixing_price(self):
        validator = DistributionValidator()

        assert await validator.validate_fixing_price(Decimal('1800.00')
                                                     ) is True
        assert await validator.validate_fixing_price(Decimal('0')) is False
        assert await validator.validate_fixing_price(Decimal('-100')) is False
        assert await validator.validate_fixing_price(Decimal('100000.01')
                                                     ) is False

    async def test_validate_system_status(self, test_db):
        validator = DistributionValidator()
        status = await validator.validate_system_status()
        assert isinstance(status, bool)

    async def test_check_database_integrity(self, test_db):
        validator = DistributionValidator()
        integrity = await validator.check_database_integrity()
        assert isinstance(integrity, bool)

    async def test_validate_distribution_result(self, test_db):
        validator = DistributionValidator()

        initial_state = {
            'money_accounts': {
                '1': '100.00'
            },
            'gold_accounts': {
                '1': '0.00'
            }
        }

        final_state = {
            'money_accounts': {
                '1': '0.00'
            },
            'gold_accounts': {
                '1': '0.05277'
            }  # (100 * 0.95) / 1800
        }

        result = await validator.validate_distribution_result(
            initial_state, final_state, Decimal('1800.00'))
        assert result is True
