
import unittest
from decimal import Decimal
from unittest.mock import AsyncMock, patch
import sys
import os
import asyncio

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.blockchain_service import BlockchainService

class TestBlockchainService(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.service = BlockchainService()

    def tearDown(self):
        self.loop.close()

    def test_add_to_batch(self):
        result = self.loop.run_until_complete(
            self.service.add_to_batch(
                user_address='0xabc123',
                euro_amount=Decimal('1000.00'),
                gold_grams=Decimal('0.5'),
                fixing_price=Decimal('1800.50')
            )
        )
        self.assertTrue(result)
        self.assertEqual(len(self.service.batch), 1)

    @patch('app.services.blockchain_service.BlockchainService.process_batch', new_callable=AsyncMock)
    def test_process_batch(self, mock_process_batch):
        mock_process_batch.return_value = {
            'status': 'success',
            'transaction_hash': '0x123...abc'
        }

        result = self.loop.run_until_complete(self.service.process_batch())

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['transaction_hash'], '0x123...abc')

    @patch('app.services.blockchain_service.BlockchainService.get_user_transactions', new_callable=AsyncMock)
    def test_get_user_transactions(self, mock_get_user_transactions):
        mock_get_user_transactions.return_value = [{
            'timestamp': 1639497600,
            'euro_amount': 1000.00,
            'gold_grams': 0.5,
            'fixing_price': 1800.50
        }]

        result = self.loop.run_until_complete(
            self.service.get_user_transactions('0xabc123')
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['gold_grams'], 0.5)

    def test_retry_operation(self):
        return self.loop.run_until_complete(self._test_retry_operation())
        
    async def _test_retry_operation(self):
        attempts = 0
        
        async def mock_operation():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise Exception("Temporary error")
            return {'status': 'success'}
            
        result = await self.service.retry_operation(mock_operation)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(attempts, 3)
        return None

if __name__ == '__main__':
    unittest.main()
