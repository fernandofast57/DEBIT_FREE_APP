
import unittest
from decimal import Decimal
from app import create_app, db
from app.models.models import User, MoneyAccount, Transaction
from app.services.batch_collection_service import BatchCollectionService

class TestBatchCollectionService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.app = create_app()
        self.app.config.update({
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'TESTING': True
        })

        async with self.app.app_context():
            await db.create_all()
            self.user = User(email='test@test.com')
            db.session.add(self.user)
            await db.session.commit()
            
            self.money_account = MoneyAccount(user_id=self.user.id)
            db.session.add(self.money_account)
            await db.session.commit()
            
            self.service = BatchCollectionService()

    async def asyncTearDown(self):
        async with self.app.app_context():
            await db.session.remove()
            await db.drop_all()

    async def test_process_bank_transfer(self):
        async with self.app.app_context():
            result = await self.service.process_bank_transfer(
                user_id=self.user.id,
                amount=Decimal('1000')
            )
            self.assertEqual(result['status'], 'success')
