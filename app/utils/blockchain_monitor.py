
import logging
from typing import Dict, Any, Optional
from web3 import Web3
from web3.middleware import geth_poa_middleware

logger = logging.getLogger(__name__)

class BlockchainMonitor:
    def __init__(self, w3: Web3):
        self.w3 = w3
        if hasattr(self.w3, 'middleware_onion'):
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.latest_block = None
        self.metrics = {
            'transactions': [],
            'gas_prices': [],
            'block_times': [],
            'network_stats': {},
            'errors': []
        }
        self.alerts = {
            'gas_price_threshold': 100,  # in Gwei
            'block_time_threshold': 30,
            'error_threshold': 5,
            'low_peer_threshold': 2
        }

    def is_gas_price_acceptable(self) -> bool:
        try:
            current_gas_price = self.w3.eth.gas_price
            gas_price_gwei = current_gas_price / 1e9  # Convert Wei to Gwei
            return gas_price_gwei < self.alerts['gas_price_threshold']
        except Exception as e:
            logger.error(f"Error checking gas price: {e}")
            return False

    async def monitor_transactions(self):
        try:
            latest_block = await self.w3.eth.get_block('latest')
            self.latest_block = latest_block
            return latest_block
        except Exception as e:
            logger.error(f"Error monitoring transactions: {e}")
            return None

    async def process_block(self, block_number: int) -> Dict[str, Any]:
        try:
            block = await self.w3.eth.get_block(block_number)
            return {
                'status': 'success',
                'transactions': block.get('transactions', [])
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    async def verify_transaction(self, tx_hash: str) -> Dict[str, Any]:
        try:
            tx = await self.w3.eth.get_transaction(tx_hash)
            if not tx or tx.get('value') is None:
                return {
                    'status': 'error',
                    'message': 'invalid transaction data'
                }
            return {
                'status': 'success',
                'transaction': tx
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def validate_transaction_amount(self, amount: float) -> bool:
        return amount > 0

    def can_process_transactions(self, transactions: list) -> bool:
        return len(transactions) > 0

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics

    def send_alert(self, message: str) -> None:
        logger.warning(f"Blockchain Alert: {message}")
