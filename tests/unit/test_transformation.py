import pytest
from decimal import Decimal
from datetime import datetime
from app.services.transformation_service import TransformationService
from app.models.models import User, MoneyAccount, GoldAccount, GoldTransformation
from app.core.exceptions import TransformationError
from unittest.mock import Mock, patch


@pytest.fixture
def transformation_service(test_db):
    return TransformationService(test_db)


@pytest.mark.asyncio
async def test_valid_transformation(transformation_service, test_db):
    # Setup
    user = User(id=1, email="test@example.com")
    money_account = MoneyAccount(user_id=1, balance=Decimal('1000.00'))
    gold_account = GoldAccount(user_id=1, balance=Decimal('0.0000'))

    test_db.add_all([user, money_account, gold_account])
    await test_db.commit()

    # Execute
    result = await transformation_service.execute_transformation(
        user_id=1,
        euro_amount=Decimal('500.00')
    )

    # Verify
    assert result['status'] == 'success'
    assert isinstance(result['gold_grams'], Decimal)
    assert result['euro_amount'] == Decimal('500.00')

    # Verify accounts
    money_account = await test_db.query(MoneyAccount).filter_by(user_id=1).first()
    gold_account = await test_db.query(GoldAccount).filter_by(user_id=1).first()

    assert money_account.balance == Decimal('500.00')
    assert gold_account.balance > Decimal('0.0000')


@pytest.mark.asyncio
async def test_amount_limits(transformation_service):
    with pytest.raises(TransformationError) as exc:
        await transformation_service.execute_transformation(1, Decimal('50.00'))
    assert "Amount must be between" in str(exc.value)

    with pytest.raises(TransformationError) as exc:
        await transformation_service.execute_transformation(1, Decimal('150000.00'))
    assert "Amount must be between" in str(exc.value)


@pytest.mark.asyncio
async def test_spread_calculation(transformation_service):
    amount = Decimal('1000.00')
    spread = transformation_service._calculate_spread(amount)
    expected = amount * (Decimal('5.0') + Decimal('1.7')) / Decimal('100')
    assert spread == expected


@pytest.mark.asyncio
async def test_insufficient_funds(transformation_service):
    user_id = 1
    amount = Decimal('1000.00')
    fixing_price = Decimal('50.00')

    mock_accounts = {
        'money': Mock(balance=Decimal('100.00')),
        'gold': Mock(balance=Decimal('0.00'))
    }

    with patch('app.services.transformation_service.MoneyAccount.get_by_user_id') as mock_money:
        mock_money.return_value = mock_accounts['money']

        with pytest.raises(ValueError) as exc_info:
            await transformation_service.execute_transformation(
                user_id=user_id,
                amount=amount,
                fixing_price=fixing_price
            )
        assert "Insufficient funds" in str(exc_info.value)


@pytest.mark.asyncio
async def test_zero_amount(transformation_service):
    with pytest.raises(ValueError) as exc_info:
        await transformation_service.execute_transformation(
            user_id=1,
            amount=Decimal('0.00'),
            fixing_price=Decimal('50.00')
        )
    assert "Amount must be greater than zero" in str(exc_info.value)