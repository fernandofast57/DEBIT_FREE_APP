
import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from app.services.transformation_service import TransformationService
from app.models import User, MoneyAccount, GoldAccount, Transaction
from app import db

class TestSystemFlow:
    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup per ogni test"""
        # Mock blockchain service
        self.blockchain_service = Mock()
        self.transformation_service = TransformationService(blockchain_service=self.blockchain_service)
        
        # Create test user and accounts
        self.user = User(
            username='test_user',
            email='test@example.com',
            blockchain_address='0x123...'
        )
        db.session.add(self.user)
        await db.session.flush()
        
        self.money_account = MoneyAccount(
            user_id=self.user.id,
            balance=Decimal('1000.00')
        )
        self.gold_account = GoldAccount(
            user_id=self.user.id,
            balance=Decimal('0')
        )
        db.session.add_all([self.money_account, self.gold_account])
        await db.session.commit()

    @pytest.mark.asyncio
    @patch('app.services.blockchain_service.BlockchainService')
    async def test_complete_flow(self, mock_blockchain_class):
        """Test del flusso completo: bonifico -> trasformazione -> bonus -> blockchain"""
        # Setup mock blockchain service
        mock_instance = Mock()
        mock_instance.add_to_batch.return_value = True
        mock_instance.process_batch.return_value = {'status': 'success', 'transaction_hash': '0x123...'}
        mock_blockchain_class.return_value = mock_instance
        
        self.transformation_service.blockchain_service = mock_instance
        
        # Test transformation
        fixing_price = Decimal('1850.00')
        result = await self.transformation_service.transform_to_gold(self.user.id, fixing_price)
        
        # Verify transformation success
        assert result['status'] == 'success'
        assert result['transaction']['original_amount'] == float(self.money_account.balance)
        assert result['transaction']['fixing_price'] == float(fixing_price)
        
        # Verify account balances
        money_account = await MoneyAccount.query.filter_by(user_id=self.user.id).first()
        gold_account = await GoldAccount.query.filter_by(user_id=self.user.id).first()
        
        assert money_account.balance == Decimal('0')
        assert gold_account.balance > Decimal('0')
        
        # Verify blockchain interaction
        mock_instance.add_to_batch.assert_called_once()
        
        # Test batch processing
        batch_result = await self.transformation_service.process_weekly_transformations(fixing_price)
        assert batch_result['status'] == 'success'
        assert batch_result['summary']['blockchain_tx'] == '0x123...'
        
    @pytest.mark.asyncio
    async def test_failed_transformation(self):
        """Test gestione errori trasformazione"""
        self.blockchain_service.add_to_batch.return_value = False
        
        result = await self.transformation_service.transform_to_gold(
            self.user.id, 
            Decimal('1850.00')
        )
        assert result['status'] == 'error'
        assert 'blockchain' in result.get('message', '').lower()
