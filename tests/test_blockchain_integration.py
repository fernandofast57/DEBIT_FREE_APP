
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch
from app import create_app, db
from app.models import User, MoneyAccount, GoldAccount
from app.services.blockchain_service import BlockchainService
from tests.test_base import BaseTest

class TestBlockchainIntegration(BaseTest):
    async def setup(self):
        await super().setup()
        self.blockchain_service = BlockchainService()
        
        async with self.app.app_context():
            # Create test user
            self.user = User(
                email='test@test.com',
                blockchain_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
            )
            db.session.add(self.user)
            await db.session.flush()

            # Create accounts
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
    async def test_batch_processing(self):
        """Test batch processing delle transazioni blockchain"""
        mock_web3 = Mock()
        self.blockchain_service.web3 = mock_web3
        
        tx_data = {
            'user_address': self.user.blockchain_address,
            'euro_amount': 1000,
            'gold_grams': 0.5,
            'fixing_price': 2000
        }
        
        result = await self.blockchain_service.add_to_batch(tx_data)
        assert result is True
        
        # Test batch processing
        mock_web3.eth.send_raw_transaction.return_value = b'0x123'
        mock_web3.eth.wait_for_transaction_receipt.return_value = {'status': 1}
        
        batch_result = await self.blockchain_service.process_batch()
        assert batch_result['status'] == 'success'
        assert 'transaction_hash' in batch_result

    @pytest.mark.asyncio
    async def test_failed_transaction(self):
        """Test gestione transazioni blockchain fallite"""
        mock_web3 = Mock()
        self.blockchain_service.web3 = mock_web3
        
        mock_web3.eth.send_raw_transaction.side_effect = Exception("Transaction failed")
        
        tx_data = {
            'user_address': self.user.blockchain_address,
            'euro_amount': 1000,
            'gold_grams': 0.5,
            'fixing_price': 2000
        }
        
        await self.blockchain_service.add_to_batch(tx_data)
        result = await self.blockchain_service.process_batch()
        assert result['status'] == 'error'
