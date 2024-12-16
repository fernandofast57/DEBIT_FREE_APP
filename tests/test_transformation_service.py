import unittest
from decimal import Decimal
from unittest.mock import Mock, patch
from app import create_app, db
from app.models.models import User, MoneyAccount, GoldAccount
from app.services.transformation_service import TransformationService
import asyncio


def async_return(result):
    """Helper per gestire risultati asincroni nei test."""
    f = asyncio.Future()
    f.set_result(result)
    return f


class TestTransformationService(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Setup utente di test e account
        self.user = User(
            email='test@test.com',
            blockchain_address='0xabc123'
        )
        db.session.add(self.user)
        db.session.flush()

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

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch('app.services.blockchain_service.BlockchainService')
    def test_transform_to_gold(self, mock_blockchain_class):
        """Test trasformazione con tracciamento blockchain"""
        mock_instance = Mock()
        mock_instance.add_to_batch.return_value = async_return(True)
        mock_blockchain_class.return_value = mock_instance

        self.service = TransformationService(blockchain_service=mock_instance)

        result = self.loop.run_until_complete(
            self.service.transform_to_gold(
                user_id=self.user.id,
                fixing_price=Decimal('1800.50')
            )
        )

        self.assertEqual(result['status'], 'success')

        # Verifica interazione con blockchain
        mock_instance.add_to_batch.assert_called_once()
        call_args = mock_instance.add_to_batch.call_args[1]

        # Verifica i parametri con tolleranza per gold_grams
        self.assertEqual(call_args['user_address'], '0xabc123')
        self.assertEqual(call_args['euro_amount'], Decimal('1000.00'))
        self.assertAlmostEqual(
            float(call_args['gold_grams']),
            0.5183,  # Valore atteso
            places=3  # Precisione aumentata a 3 cifre decimali
        )
        self.assertEqual(call_args['fixing_price'], Decimal('1800.50'))

    @patch('app.services.blockchain_service.BlockchainService')
    def test_weekly_batch_processing(self, mock_blockchain):
        """Test processo batch settimanale con blockchain"""
        mock_instance = mock_blockchain.return_value
        mock_instance.add_to_batch.return_value = async_return(True)
        mock_instance.process_batch.return_value = async_return({
            'status': 'success',
            'transaction_hash': '0x123...abc'
        })

        self.service = TransformationService(blockchain_service=mock_instance)

        result = self.loop.run_until_complete(
            self.service.process_weekly_transformations(
                fixing_price=Decimal('1800.50')
            )
        )

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['summary']['blockchain_tx'], '0x123...abc')

    @patch('app.services.blockchain_service.BlockchainService')
    def test_transformation_history(self, mock_blockchain):
        """Test recupero storico trasformazioni con blockchain"""
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

        self.service = TransformationService(blockchain_service=mock_instance)

        # Crea una trasformazione
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

        self.assertEqual(history_result['status'], 'success')
        self.assertEqual(len(history_result['blockchain_history']), 1)
        self.assertEqual(
            history_result['blockchain_history'][0]['fixing_price'], 1800.50
        )


if __name__ == '__main__':
    unittest.main()


