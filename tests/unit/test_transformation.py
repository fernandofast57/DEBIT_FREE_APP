
import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import patch, MagicMock
from app.services.gold.weekly_distribution import WeeklyGoldDistribution
from app.models.models import User, MoneyAccount, GoldAccount, Transaction
from app.database import db

@pytest.mark.asyncio
class TestGoldTransformation:
    @pytest.fixture
    def distribution_service(self):
        return WeeklyGoldDistribution()
    
    @pytest.fixture
    def mock_fixing_price(self):
        return Decimal('1800.00')
        
    async def test_complete_transformation_flow(self, test_db, test_user, distribution_service, mock_fixing_price):
        """Test the complete transformation flow from EUR to gold"""
        # 1. Pre-transformation checks
        initial_money = Decimal('1000.00')
        initial_gold = Decimal('0.00')
        
        with db.session() as session:
            # Verify initial balances
            user = session.query(User).filter_by(id=test_user.id).first()
            assert user.money_account.balance == initial_money
            assert user.gold_account.balance == initial_gold
            
            # 2. Execute transformation
            result = await distribution_service.process_distribution(mock_fixing_price)
            
            # 3. Verify transformation results
            assert result['status'] == 'success'
            assert Decimal(str(result['total_euro'])) == initial_money
            
            # 4. Verify final balances
            session.refresh(user)
            assert user.money_account.balance == Decimal('0.00')
            assert user.gold_account.balance > Decimal('0.00')
            
            # 5. Verify transaction record
            transaction = session.query(Transaction).filter_by(user_id=user.id).first()
            assert transaction is not None
            assert transaction.amount == initial_money
            assert transaction.type == 'transformation'

    @pytest.mark.asyncio
    async def test_transformation_validation(self, distribution_service, mock_fixing_price):
        """Test validation of transformation parameters"""
        with pytest.raises(ValueError):
            await distribution_service.process_distribution(Decimal('-1800.00'))
            
        with pytest.raises(ValueError):
            await distribution_service.process_distribution(Decimal('0.00'))

    @pytest.mark.asyncio
    async def test_transformation_with_fees(self, test_db, test_user, distribution_service, mock_fixing_price):
        """Test transformation with fee calculation"""
        structure_fee = Decimal('0.05')  # 5% come definito in TransformationService
        initial_amount = Decimal('1000.00')
        
        with db.session() as session:
            result = await distribution_service.process_distribution(mock_fixing_price)
            
            user = session.query(User).filter_by(id=test_user.id).first()
            expected_gold = (initial_amount * (1 - structure_fee)) / mock_fixing_price
            
            assert abs(user.gold_account.balance - expected_gold) < Decimal('0.0001')
