
import unittest
from decimal import Decimal
from app import create_app, db
from app.models.models import User, MoneyAccount, Transaction
from app.services.batch_collection_service import BatchCollectionService
import asyncio

class TestBatchCollectionService(unittest.TestCase):
    async def asyncSetUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        await self.app_context.push()
        await db.create_all()

        self.user = User(email='test@test.com')
        db.session.add(self.user)
        await db.session.commit()

        self.money_account = MoneyAccount(user_id=self.user.id)
        db.session.add(self.money_account)
        await db.session.commit()

        self.service = BatchCollectionService()

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

    def test_process_bank_transfer(self):
        async def run_test():
            result = await self.service.process_bank_transfer(
                user_id=self.user.id,
                amount=Decimal('1000')
            )
            self.assertEqual(result['status'], 'success')
        
        self.loop.run_until_complete(run_test())
