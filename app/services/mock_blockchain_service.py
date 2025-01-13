# app/services/mock_blockchain_service.py
from unittest.mock import Mock
from web3 import Web3

class MockBlockchainService:
    def __init__(self):
        self.w3 = Mock(spec=Web3)
        self.setup_mocks()
        self.is_initialized = True

    def setup_mocks(self):
        self.w3.eth = Mock()
        self.w3.eth.get_block_number = Mock(return_value=12345)
        self.w3.eth.wait_for_transaction_receipt = Mock(return_value=Mock(status=1))
        self.w3.is_connected = Mock(return_value=True)
        self.w3.eth.gas_price = 20000000000
        self.w3.eth.chain_id = 80001

    async def transform_gold(self, user_id, amount):
        return {
            'status': 'verified',
            'transaction_hash': '0x123',
            'block_number': 12345
        }

    async def distribute_bonus(self, user_id, amount):
        if not self.is_initialized:
            raise Exception('Blockchain connection or account not initialized')
        return {
            'status': 'verified',
            'transaction_hash': '0x456',
            'block_number': 12346
        }

    async def update_noble_rank(self, address, rank):
        return {
            'status': 'verified',
            'transaction_hash': '0x123',
            'block_number': 12345
        }

    async def record_gold_transaction(self, user_address, euro_amount, gold_grams):
        return {
            'status': 'verified',
            'transaction_hash': '0x456',
            'block_number': 12346
        }

    def get_verification_status(self, transaction_hash):
        return 'verified'