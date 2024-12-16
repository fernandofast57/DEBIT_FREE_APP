
import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from app import create_app, db
from app.models.models import User, MoneyAccount, GoldAccount
from app.services.transformation_service import TransformationService
from app.models.noble_system import NobleRank

class TestSystemFlow:
    @pytest.fixture(autouse=True)
    async def setup_app(self):
        """Setup l'applicazione e il database"""
        self.app = create_app()
        self.app.config.update({
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db',
            'TESTING': True,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False
        })

        async with self.app.app_context():
            await db.create_all()
            
            # Setup test user
            self.user = User(email='test@test.com')
            db.session.add(self.user)
            await db.session.commit()
            
            # Setup transformation service
            self.transformation_service = TransformationService()
            
            await self._setup_accounts()

            yield

            await db.session.remove()
            await db.session.execute('DELETE FROM gold_accounts')
            await db.session.execute('DELETE FROM money_accounts')
            await db.session.execute('DELETE FROM users')
            await db.session.commit()
            await db.drop_all()

    async def _setup_accounts(self):
        """Setup conti denaro e oro per ogni utente"""
        money_account = MoneyAccount(
            user_id=self.user.id,
            balance=Decimal('1000.00')
        )
        gold_account = GoldAccount(
            user_id=self.user.id,
            balance=Decimal('0')
        )
        db.session.add_all([money_account, gold_account])
        await db.session.commit()

    @pytest.mark.asyncio
    @patch('app.services.blockchain_service.BlockchainService')
    async def test_complete_flow(self, mock_blockchain_class):
        """Test del flusso completo: bonifico -> trasformazione -> bonus -> blockchain"""
        mock_instance = Mock()
        mock_instance.add_to_batch.return_value = True
        mock_instance.process_batch.return_value = {'status': 'success', 'transaction_hash': '0x123...'}
        mock_blockchain_class.return_value = mock_instance

        self.transformation_service.blockchain_service = mock_instance

        async with self.app.app_context():
            result = await self.transformation_service.transform_to_gold(
                user_id=self.user.id,
                fixing_price=Decimal('1800.50')
            )
            
            assert result['status'] == 'success'
            mock_instance.add_to_batch.assert_called_once()
