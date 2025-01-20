import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock
from app.services.transformation_service import TransformationService
from app.models.models import User, MoneyAccount, GoldAccount

@pytest.mark.asyncio
class TestTransformationService:
    @pytest.fixture
    def mock_fixing_price(self):
        return Decimal('50.00')

    async def test_verify_transfer_valid(self, test_user, test_db):
        """Test valid transfer verification"""
        amount = Decimal('100.00')
        result = await TransformationService.verify_transfer(test_user.id, amount)
        assert result['valid'] is True
        assert 'user' in result

    async def test_verify_transfer_invalid_amount(self, test_user, test_db):
        """Test invalid amount verification"""
        amount = Decimal('-100.00')
        result = await TransformationService.verify_transfer(test_user.id, amount)
        assert result['valid'] is False
        assert result['reason'] == "Invalid amount"

    async def test_process_organization_fee(self):
        """Test organization fee calculation"""
        amount = Decimal('1000.00')
        expected_fee = amount * TransformationService.ORGANIZATION_FEE
        net_amount = await TransformationService.process_organization_fee(amount)
        assert net_amount == (amount - expected_fee)

    async def test_transform_gold_success(self, test_user, mock_fixing_price):
        """Test successful gold transformation"""
        euro_amount = Decimal('100.00')
        result = await TransformationService.process_transformation(
            test_user.id,
            euro_amount,
            mock_fixing_price
        )
        assert result['status'] == 'success'
        assert 'gold_grams' in result

    async def test_transform_gold_insufficient_funds(self, test_user, mock_fixing_price):
        """Test transformation with insufficient funds"""
        euro_amount = Decimal('2000.00')  # More than test_user balance
        result = await TransformationService.process_transformation(
            test_user.id,
            euro_amount,
            mock_fixing_price
        )
        assert result['status'] == 'error'
        assert 'Insufficient funds' in result['message']