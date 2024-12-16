import unittest
from decimal import Decimal
from unittest.mock import Mock, patch
from app import create_app, db
from app.models.models import User, MoneyAccount, GoldAccount
from app.services.transformation_service import TransformationService
import asyncio

def async_return(result):
    f = asyncio.Future()
    f.set_result(result)
    return f

class TestBlockchainIntegration(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Setup test user con indirizzo blockchain
        self.user = User(
            email='test@test.com',
            blockchain_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        db.session.add(self.user)
        db.session.flush()

        # Setup accounts
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

        # Inizializza il servizio
        self.service = TransformationService()

        # Setup loop asincrono per i test
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch('app.services.blockchain_service.BlockchainService')
    def test_transform_with_blockchain(self, mock_blockchain_class):
        """Test trasformazione con tracciamento blockchain"""
        # Setup mock blockchain service
        mock_instance = Mock()
        mock_instance.add_to_batch.return_value = async_return(True)
        mock_blockchain_class.return_value = mock_instance

        # Reset service per usare il mock
        self.service.blockchain_service = mock_instance

        # Esegui trasformazione
        result = self.loop.run_until_complete(
            self.service.transform_to_gold(
                user_id=self.user.id,
                fixing_price=Decimal('1800.50')
            )
        )

        # Verifica risultato
        self.assertEqual(result['status'], 'success')

        # Verifica chiamata blockchain
        mock_instance.add_to_batch.assert_called_once()
        call_args = mock_instance.add_to_batch.call_args[1]
        self.assertEqual(call_args['user_address'], self.user.blockchain_address)
        self.assertAlmostEqual(float(call_args['fixing_price']), 1800.50)

    @patch('app.services.blockchain_service.BlockchainService')
    def test_weekly_batch_processing(self, mock_blockchain):
        """Test processo batch settimanale con blockchain"""
        # Setup mock blockchain service
        mock_instance = mock_blockchain.return_value
        mock_instance.add_to_batch.return_value = async_return(True)
        mock_instance.process_batch.return_value = async_return({
            'status': 'success',
            'transaction_hash': '0x123...abc'
        })

        # Esegui processo batch
        result = self.loop.run_until_complete(
            self.service.process_weekly_transformations(
                fixing_price=Decimal('1800.50')
            )
        )

        # Verifica risultato
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['summary']['success_count'], 1)
        self.assertEqual(result['summary']['blockchain_tx'], '0x123...abc')

        # Verifica chiamate blockchain
        mock_instance.add_to_batch.assert_called_once()
        mock_instance.process_batch.assert_called_once()

    @patch('app.services.blockchain_service.BlockchainService')
    def test_transformation_history(self, mock_blockchain):
        """Test recupero storico trasformazioni con blockchain"""
        # Setup mock blockchain service
        mock_instance = mock_blockchain.return_value
        mock_instance.add_to_batch.return_value = async_return(True)
        mock_instance.get_user_transactions.return_value = async_return([
            {
                'timestamp': 1639497600,
                'euro_amount': Decimal('1000.00'),
                'gold_grams': Decimal('0.5'),
                'fixing_price': Decimal('1800.50')
            }
        ])

        # Prima crea una trasformazione
        self.loop.run_until_complete(
            self.service.transform_to_gold(
                user_id=self.user.id,
                fixing_price=Decimal('1800.50')
            )
        )

        # Recupera storico
        history_result = self.loop.run_until_complete(
            self.service.get_transformation_history(self.user.id)
        )

        # Verifica risultato
        self.assertEqual(history_result['status'], 'success')
        self.assertEqual(len(history_result['history']), 1)  # DB history
        self.assertEqual(len(history_result['blockchain_history']), 1)  # Blockchain history

        # Verifica chiamata blockchain
        mock_instance.get_user_transactions.assert_called_once_with(
            self.user.blockchain_address
        )

if __name__ == '__main__':
    unittest.main()
