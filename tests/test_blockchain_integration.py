
import unittest
from decimal import Decimal
from unittest.mock import AsyncMock, patch
import asyncio
from app import create_app, db
from app.services.blockchain_service import BlockchainService

class TestBlockchainIntegration(unittest.TestCase):
    async def asyncSetUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        await self.app_context.push()
        await db.create_all()
        self.service = BlockchainService()

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

    def test_blockchain_operations(self):
        async def run_test():
            result = await self.service.add_to_batch(
                user_address='0xabc123',
                euro_amount=Decimal('1000.00'),
                gold_grams=Decimal('0.5'),
                fixing_price=Decimal('1800.50')
            )
            self.assertTrue(result)
            self.assertEqual(len(self.service.batch), 1)
        
        self.loop.run_until_complete(run_test())
