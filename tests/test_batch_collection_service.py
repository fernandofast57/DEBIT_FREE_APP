
import unittest
from decimal import Decimal
from app import create_app, db
from app.models.models import User, MoneyAccount, Transaction
from app.services.batch_collection_service import BatchCollectionService
import asyncio

class TestBatchCollectionService(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app.config['TESTING'] = True
        
        self.loop.run_until_complete(self._async_setup())
        
    async def _async_setup(self):
        async with self.app.app_context():
            await db.create_all()
            
            self.user = User(email='test@test.com')
            db.session.add(self.user)
            await db.session.commit()
            
            self.money_account = MoneyAccount(user_id=self.user.id)
            db.session.add(self.money_account)
            await db.session.commit()
            
            self.service = BatchCollectionService()

    def tearDown(self):
        self.loop.run_until_complete(self._async_teardown())
        self.loop.close()

    async def _async_teardown(self):
        async with self.app.app_context():
            await db.session.remove()
            await db.drop_all()

    def test_process_bank_transfer(self):
        async def run_test():
            async with self.app.app_context():
                result = await self.service.process_bank_transfer(
                    user_id=self.user.id,
                    amount=Decimal('1000')
                )
                self.assertEqual(result['status'], 'success')
        
        self.loop.run_until_complete(run_test())
