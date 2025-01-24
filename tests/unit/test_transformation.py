
import pytest
import asyncio
from decimal import Decimal
from datetime import datetime
from app.services.transformation_service import TransformationService
from app.models.models import User, MoneyAccount, GoldAccount
from unittest.mock import Mock, patch

@pytest.fixture
def transformation_service():
    return TransformationService()

@pytest.mark.asyncio
async def test_valid_transformation(transformation_service):
    # Setup
    user_id = 1
    amount = Decimal('100.00')
    fixing_price = Decimal('50.00')
    
    mock_accounts = {
        'money': Mock(balance=Decimal('100.00')),
        'gold': Mock(balance=Decimal('0.00'))
    }
    
    with patch('app.services.transformation_service.MoneyAccount.get_by_user_id') as mock_money:
        with patch('app.services.transformation_service.GoldAccount.get_by_user_id') as mock_gold:
            mock_money.return_value = mock_accounts['money']
            mock_gold.return_value = mock_accounts['gold']
            
            result = await transformation_service.execute_transformation(
                user_id=user_id,
                amount=amount,
                fixing_price=fixing_price
            )
            
            assert result['status'] == 'success'
            assert result['amount'] == amount
            assert 'transaction_id' in result

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
