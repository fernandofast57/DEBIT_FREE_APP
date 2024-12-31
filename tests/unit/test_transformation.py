
import pytest
from decimal import Decimal
from app.services.transformation_service import TransformationService
from app.models.models import User, MoneyAccount, GoldAccount

@pytest.mark.asyncio
async def test_transformation_calculates_correct_gold_amount(app):
    # Arrange
    with app.app_context():
        service = TransformationService()
        euro_amount = Decimal('100.00')
        fixing_price = Decimal('50.00')
        expected_gold = Decimal('1.90')  # (100 - 5% fee) / 50

        # Create test user with required accounts
        test_user = User(id=1)
        test_user.money_account = MoneyAccount()
        test_user.gold_account = GoldAccount()
        
        # Mock the user query
        async def mock_get(user_id):
            return test_user
        User.query.get = mock_get

        # Act
        result = await service.process_transformation(1, euro_amount, fixing_price)

        # Assert
        assert result['status'] == 'success'
        assert Decimal(str(result['gold_grams'])) == expected_gold
