
from unittest.mock import Mock
from web3 import Web3
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class MockBlockchainService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MockBlockchainService, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if not self.initialized:
            self.w3 = Mock(spec=Web3)
            self.setup_mocks()
            self.initialized = True
            logger.info("MockBlockchainService initialized")

    def setup_mocks(self):
        self.w3.eth = Mock()
        self.w3.eth.get_block_number = Mock(return_value=12345)
        self.w3.eth.wait_for_transaction_receipt = Mock(return_value=Mock(status=1))
        self.w3.is_connected = Mock(return_value=True)
        self.w3.eth.gas_price = 20000000000
        self.w3.eth.chain_id = 80001
        self.w3.eth.account = Mock()
        self.w3.eth.account.sign_transaction = Mock(
            return_value=Mock(rawTransaction=b'0x456', hash=b'0x123'))
        self.contract = Mock()
        self.account = Mock(address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e', 
                          privateKey=b'0x123')

    def is_connected(self) -> bool:
        return True

    async def initialize(self) -> None:
        if not self.initialized:
            self.setup_mocks()
            self.initialized = True

    async def send_transaction(self, func_call: Any, value: int = 0) -> Dict[str, Any]:
        return {
            'status': 'verified',
            'transaction_hash': '0x123',
            'block_number': 12345
        }

    async def update_noble_rank(self, address: str, rank: int) -> Dict[str, Any]:
        return await self.send_transaction(None)

    async def record_gold_transaction(self, address: str, euro_amount: float, 
                                    gold_grams: float) -> Dict[str, Any]:
        return await self.send_transaction(None)

    async def get_transaction_stats(self) -> Dict[str, Any]:
        return {
            'status': 'verified',
            'stats': {
                'gas_price': 20000000000,
                'block_number': 12345,
                'network_id': 80001,
                'connected': True,
                'syncing': False,
                'peer_count': 1
            }
        }
