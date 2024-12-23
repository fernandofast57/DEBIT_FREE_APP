import unittest
from app import create_app, db
from app.services.batch_collection_service import BatchCollectionService

class TestBatchCollectionService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app.config['TESTING'] = True
        self.service = BatchCollectionService()

        async with self.app.app_context():
            await db.create_all()

    async def asyncTearDown(self):
        async with self.app.app_context():
            await db.drop_all()
            db.session.remove()

    async def test_process_batch_transfers(self):
        """Test processing multiple transfers in a batch"""
        async with self.app.app_context():
            batch_transfers = [
                {'user_id': 1, 'amount': '1000.00', 'reference': 'TEST-001'},
                {'user_id': 2, 'amount': '2000.00', 'reference': 'TEST-002'}
            ]
            
            result = await self.service.process_batch_transfers(batch_transfers)
            assert result['status'] == 'success'
            assert 'tx_hash' in result
            
            # Verify transactions in database
            transactions = Transaction.query.all()
            assert len(transactions) == 2
            assert all(t.status == 'completed' for t in transactions)

    async def test_invalid_gold_transfer(self):
        """Test invalid gold transfer according to glossary rules"""
        async with self.app.app_context():
            invalid_batch = [
                {'user_id': 1, 'amount': 'invalid', 'reference': 'TEST-003'}
            ]
            
            result = await self.service.process_batch_transfers(invalid_batch)
            assert result['status'] == 'error'
            assert 'message' in result

    async def test_empty_transaction_batch(self):
        """Test empty transaction batch handling"""
        async with self.app.app_context():
            result = await self.service.process_batch_transfers([])
            assert result['status'] == 'error'
            assert 'message' in result

    async def test_large_transaction_batch(self):
        """Test large transaction batch processing"""
        async with self.app.app_context():
            large_batch = [
                {'user_id': i, 'amount': '100.00', 'reference': f'TEST-{i}'}
                for i in range(1, 101)
            ]
            result = await self.service.process_batch_transfers(large_batch)
            assert result['status'] == 'success'
            assert 'tx_hash' in result

    async def test_duplicate_transaction_references(self):
        """Test duplicate transaction references as per glossary definition"""
        async with self.app.app_context():
            batch = [
                {'user_id': 1, 'amount': '100.00', 'reference': 'TEST-DUP'},
                {'user_id': 2, 'amount': '200.00', 'reference': 'TEST-DUP'}
            ]
            result = await self.service.process_batch_transfers(batch)
            assert result['status'] == 'success'
            transactions = Transaction.query.filter_by(reference='TEST-DUP').all()
            assert len(transactions) == 2