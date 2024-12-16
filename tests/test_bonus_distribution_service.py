
import unittest
from decimal import Decimal
from app import create_app, db
from app.models.models import User, MoneyAccount
from app.models.noble_system import NobleRank, NobleRelation, BonusTransaction
from app.services.bonus_distribution_service import BonusDistributionService
import asyncio

class TestBonusDistributionService(unittest.TestCase):
    async def asyncSetUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        await self.app_context.push()
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

        self.accounts = [
            MoneyAccount(user_id=user.id, balance=Decimal('0'))
            for user in [self.user1, self.user2, self.user3, self.user4]
        ]
        db.session.add_all(self.accounts)
        await db.session.commit()

        self.relations = [
            NobleRelation(referred_id=self.user1.id, referrer_id=self.user2.id, rank_id=self.nobile.id),
            NobleRelation(referred_id=self.user2.id, referrer_id=self.user3.id, rank_id=self.visconte.id),
            NobleRelation(referred_id=self.user3.id, referrer_id=self.user4.id, rank_id=self.conte.id)
        ]
        db.session.add_all(self.relations)
        await db.session.commit()

        self.service = BonusDistributionService()

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

    def test_bonus_distribution(self):
        async def run_test():
            result = await self.service.distribute_transaction_bonus(
                self.user1.id,
                Decimal('1000')
            )
            self.assertEqual(result['status'], 'success')
            self.assertEqual(len(result['distributions']), 3)
            
        self.loop.run_until_complete(run_test())
