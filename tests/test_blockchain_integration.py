import unittest
from decimal import Decimal
from unittest.mock import Mock, patch
from app import create_app, db
from app.models.models import User, MoneyAccount, GoldAccount
from app.services.transformation_service import TransformationService
import asyncio
from contextlib import contextmanager
from flask import current_app

def async_return(result):
    f = asyncio.Future()
    f.set_result(result)
    return f

class TestBlockchainIntegration(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """Setup una volta per tutti i test"""
        cls.app = create_app()
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        cls.app.config['TESTING'] = True
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Cleanup alla fine di tutti i test"""
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        """Setup per ogni test"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Setup test user
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

    def tearDown(self):
        """Cleanup dopo ogni test"""
        self.loop.close()
        db.session.query(GoldAccount).delete()
        db.session.query(MoneyAccount).delete()
        db.session.query(User).delete()
        db.session.commit()

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

if __name__ == '__main__':
    unittest.main()