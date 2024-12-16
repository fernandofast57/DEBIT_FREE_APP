
import unittest
from app import create_app, db
from app.services.blockchain_service import BlockchainService

class TestBlockchainIntegration(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app.config['TESTING'] = True
        self.service = BlockchainService()

        async with self.app.app_context():
            await db.create_all()

    async def asyncTearDown(self):
        async with self.app.app_context():
            await db.drop_all()
            db.session.remove()
