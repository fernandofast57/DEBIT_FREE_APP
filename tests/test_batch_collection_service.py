
import unittest
from decimal import Decimal
from app import create_app, db
from app.models.models import User, MoneyAccount, Transaction
import asyncio

class TestBatchCollectionService(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        db.create_all()

        # Setup test user and account
        self.user = User(email='test@test.com')
        db.session.add(self.user)
        db.session.commit()

        self.money_account = MoneyAccount(user_id=self.user.id)
        db.session.add(self.money_account)
        db.session.commit()

    def tearDown(self):
        self.loop.close()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    async def async_test_process_bank_transfer(self):
        result = await self.service.process_bank_transfer(
            user_id=self.user.id,
            amount=Decimal('1000')
        )
        self.assertEqual(result['status'], 'success')
        
    def test_process_bank_transfer(self):
        self.loop.run_until_complete(self.async_test_process_bank_transfer())
