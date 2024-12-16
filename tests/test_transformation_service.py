
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

class TestTransformationService(unittest.TestCase):
    async def asyncSetUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        await self.app_context.push()
        await db.create_all()

        self.user = User(
            email='test@test.com',
            blockchain_address='0xabc123'
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

    async def asyncTearDown(self):
        await db.session.remove()
        await db.drop_all()
        await self.app_context.pop()

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.asyncSetUp())

    def tearDown(self):
        self.loop.run_until_complete(self.asyncTearDown())
        self.loop.close()

    @patch('app.services.blockchain_service.BlockchainService')
    def test_transform_to_gold(self, mock_blockchain_class):
        async def run_test():
            mock_instance = Mock()
            mock_instance.add_to_batch.return_value = async_return(True)
            mock_blockchain_class.return_value = mock_instance

            service = TransformationService(blockchain_service=mock_instance)
            result = await service.transform_to_gold(
                user_id=self.user.id,
                fixing_price=Decimal('1800.50')
            )

            self.assertEqual(result['status'], 'success')
            mock_instance.add_to_batch.assert_called_once()

        self.loop.run_until_complete(run_test())
