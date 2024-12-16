
import unittest
from decimal import Decimal
from app import create_app, db
from app.models.models import User, MoneyAccount
from app.models.noble_system import NobleRank, NobleRelation, BonusTransaction
from app.services.bonus_distribution_service import BonusDistributionService

class TestBonusDistributionService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.app = create_app()
        self.app.config.update({
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'TESTING': True
        })

        async with self.app.app_context():
            await db.create_all()

            self.nobile = NobleRank(title='Nobile', bonus_rate=Decimal('0.007'), level=1)
            self.visconte = NobleRank(title='Visconte', bonus_rate=Decimal('0.005'), level=2)
            self.conte = NobleRank(title='Conte', bonus_rate=Decimal('0.005'), level=3)

            db.session.add_all([self.nobile, self.visconte, self.conte])
            await db.session.commit()

            self.user1 = User(email='user1@test.com')
            self.user2 = User(email='user2@test.com')
            self.user3 = User(email='user3@test.com')
            self.user4 = User(email='user4@test.com')

            db.session.add_all([self.user1, self.user2, self.user3, self.user4])
            await db.session.commit()

    async def asyncTearDown(self):
        async with self.app.app_context():
            await db.session.remove()
            await db.drop_all()
