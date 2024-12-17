
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch
from app import create_app, db
from app.models.models import User, MoneyAccount, GoldAccount
from app.models.noble_system import NobleRank, NobleRelation
from app.services.transformation_service import TransformationService
from app.services.blockchain_service import BlockchainService
from app.services.bonus_distribution_service import BonusDistributionService
from app.services.batch_collection_service import BatchCollectionService

class TestCompleteSystem:
    @pytest.fixture
    async def setup_test_env(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        
        async with app.app_context():
            await db.create_all()
            
            # Create test user
            self.user = User(
                email='test@example.com',
                blockchain_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
            )
            db.session.add(self.user)
            await db.session.flush()
            
            # Create accounts
            self.money_account = MoneyAccount(user_id=self.user.id, balance=Decimal('1000.00'))
            self.gold_account = GoldAccount(user_id=self.user.id, balance=Decimal('0'))
            db.session.add_all([self.money_account, self.gold_account])
            
            # Setup noble ranks
            ranks = [
                NobleRank(title='Nobile', bonus_rate=Decimal('0.007'), level=1),
                NobleRank(title='Visconte', bonus_rate=Decimal('0.005'), level=2),
                NobleRank(title='Conte', bonus_rate=Decimal('0.005'), level=3)
            ]
            db.session.add_all(ranks)
            await db.session.commit()
            
            yield app
            
            await db.session.remove()
            await db.drop_all()

    @pytest.mark.asyncio
    async def test_complete_system_flow(self, setup_test_env):
        """Test the complete system flow: Transfer -> Transform -> Bonus -> Blockchain"""
        
        # 1. Test Bank Transfer
        batch_service = BatchCollectionService()
        transfer_result = batch_service.process_bank_transfer(
            self.user.id, 
            Decimal('500.00')
        )
        assert transfer_result['status'] == 'success'
        assert self.money_account.balance == Decimal('1500.00')
        
        # 2. Test Transformation
        mock_blockchain = Mock()
        mock_blockchain.add_to_batch.return_value = True
        mock_blockchain.process_batch.return_value = {
            'status': 'success',
            'transaction_hash': '0x123'
        }
        
        transformation_service = TransformationService(blockchain_service=mock_blockchain)
        transform_result = await transformation_service.transform_to_gold(
            self.user.id,
            Decimal('1800.50')  # Current fixing price
        )
        
        assert transform_result['status'] == 'success'
        assert transform_result['transaction']['gold_grams'] > 0
        
        # 3. Test Bonus Distribution
        bonus_service = BonusDistributionService()
        bonus_result = bonus_service.distribute_transaction_bonus(
            self.user.id,
            Decimal('1500.00')
        )
        
        assert bonus_result['status'] == 'success'
        
        # 4. Test Transaction History
        history = await transformation_service.get_transformation_history(self.user.id)
        assert history['status'] == 'success'
        assert len(history['history']) > 0
        
        # 5. Verify Final State
        user = await db.session.get(User, self.user.id)
        money_account = MoneyAccount.query.filter_by(user_id=self.user.id).first()
        gold_account = GoldAccount.query.filter_by(user_id=self.user.id).first()
        
        assert money_account.balance == Decimal('0')  # Should be 0 after transformation
        assert gold_account.balance > 0  # Should have gold after transformation
