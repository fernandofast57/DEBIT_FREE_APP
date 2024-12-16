
import unittest
from decimal import Decimal
from unittest.mock import Mock, patch
from app import create_app, db
from app.models.models import User, MoneyAccount, GoldAccount
from app.services.transformation_service import TransformationService

class TestTransformationService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.app = create_app()
        self.app.config.update({
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'TESTING': True
        })

        async with self.app.app_context():
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
        async with self.app.app_context():
            await db.session.remove()
            await db.drop_all()
