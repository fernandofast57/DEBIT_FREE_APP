
from typing import Dict, Any, List
from decimal import Decimal
import logging
from web3 import Web3

logger = logging.getLogger(__name__)

class BlockchainMonitor:
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.last_processed_block = 0
        self.alerts = []

    async def monitor_transactions(self, transaction_data: Dict) -> Dict:
        try:
            self.alerts.append({
                'type': transaction_data['type'],
                'status': transaction_data['status'],
                'tx_hash': transaction_data['tx_hash']
            })
            return {'status': 'monitored'}
        except Exception as e:
            logger.error(f"Error monitoring transaction: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def validate_transaction_amount(self, amount: Decimal) -> bool:
        return amount > Decimal('0') and amount < Decimal('1000000.0')

    def can_process_transactions(self, transactions: List[str]) -> bool:
        return True if transactions else False

    def is_gas_price_acceptable(self) -> bool:
        try:
            current_price = self.w3.eth.gas_price
            max_price = 1_000_000_000_000
            return current_price < max_price
        except Exception as e:
            logger.error(f"Error checking gas price: {str(e)}")
            return True

    def send_alert(self, message: str) -> Dict:
        self.alerts.append(message)
        return {'status': 'sent', 'message': message}

    def check_new_blocks(self) -> bool:
        current_block = self.w3.eth.get_block_number()
        return current_block > self.last_processed_block
