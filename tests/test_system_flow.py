import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from app import create_app, db
from app.models.models import User, MoneyAccount, GoldAccount
from app.services.transformation_service import TransformationService


class TestSystemFlow:
    @pytest.fixture(autouse=True)
    async def setup_app(self):
        """Setup l'applicazione e il database"""
        # Inizializza l'applicazione
        self.app = create_app()
        self.app.config.update({
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db',
            'TESTING': True,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False
        })

        # Crea il database e gli utenti
        async with self.app.app_context():
            db.create_all()

            # Inizializza un utente di test
            self.user = User(
                email='test@test.com',
                blockchain_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
            )
            db.session.add(self.user)
            db.session.commit()

            # Crea i conti associati
            self.money_account = MoneyAccount(
                user_id=self.user.id,
                balance=Decimal('1000.00')
            )
            self.gold_account = GoldAccount(
                user_id=self.user.id,
                balance=Decimal('0')
            )
            db.session.add_all([self.money_account, self.gold_account])
            db.session.commit()

            # Inizializza il servizio TransformationService
            self.blockchain_service = Mock()
            self.transformation_service = TransformationService(blockchain_service=self.blockchain_service)

            yield  # Cleanup finale
            db.session.remove()
            db.drop_all()

    @pytest.mark.asyncio
    @patch('app.services.blockchain_service.BlockchainService')
    @patch('app.services.bonus_distribution_service.BonusDistributionService')
    @patch('app.models.models.User')
    async def test_complete_flow(self, mock_user_class, mock_bonus_class, mock_blockchain_class):
        """Test del flusso completo: bonifico -> trasformazione -> bonus -> blockchain"""
        # Configura il mock per User
        mock_user = Mock()
        mock_user.id = self.user.id
        mock_user.blockchain_address = self.user.blockchain_address
        mock_user_class.query.get.return_value = mock_user

        # Configura il mock per BlockchainService
        mock_blockchain = Mock()
        mock_blockchain.add_to_batch.return_value = True
        mock_blockchain.process_batch.return_value = {'status': 'success', 'transaction_hash': '0x123...'}
        mock_blockchain_class.return_value = mock_blockchain

        # Configura il mock per BonusDistributionService
        mock_bonus = Mock()
        mock_bonus.distribute_transaction_bonus.return_value = {
            'status': 'success',
            'total_distributed': 50.0,
            'distributions': [
                {'user_id': 1, 'bonus_amount': 30.0, 'rank_id': 1},
                {'user_id': 2, 'bonus_amount': 20.0, 'rank_id': 2}
            ]
        }
        mock_bonus_class.return_value = mock_bonus

        self.transformation_service.blockchain_service = mock_blockchain

        # Simula la trasformazione
        async with self.app.app_context():
            fixing_price = Decimal('1800.50')
            result = await self.transformation_service.transform_to_gold(
                user_id=self.user.id,
                fixing_price=fixing_price
            )

            # Verifica il risultato della trasformazione
            assert result['status'] == 'success'
            assert result['transaction']['fixing_price'] == float(fixing_price)
            assert 'gold_grams' in result['transaction']

            # Verifica che il saldo sia stato aggiornato
            money_account = MoneyAccount.query.filter_by(user_id=self.user.id).first()
            assert money_account.balance == 0

            # Verifica la chiamata alla blockchain
            mock_blockchain.add_to_batch.assert_called_once()
            mock_blockchain.process_batch.assert_called_once()
