
import logging
from datetime import datetime
from typing import Dict, Any
from web3 import Web3
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

class BlockchainMonitor:
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.metrics = {
            'transactions': [],
            'gas_prices': [],
            'block_times': [],
            'errors': []
        }
        self.alerts = {
            'gas_price_threshold': 100,  # in gwei
            'block_time_threshold': 30,  # in seconds
            'error_threshold': 5  # max errors before alert
        }

    def monitor_transactions(self, transaction_data: Dict[str, Any]) -> None:
        try:
            timestamp = datetime.utcnow().isoformat()
            gas_price = self.w3.eth.gas_price
            
            self.metrics['transactions'].append({
                'timestamp': timestamp,
                'type': transaction_data.get('type', 'unknown'),
                'status': transaction_data.get('status', 'unknown'),
                'tx_hash': transaction_data.get('tx_hash', ''),
                'gas_price': gas_price
            })

            if gas_price > self.w3.to_wei(self.alerts['gas_price_threshold'], 'gwei'):
                self.send_alert(f"High gas price detected: {self.w3.from_wei(gas_price, 'gwei')} gwei")

            # Keep only last 100 transactions
            if len(self.metrics['transactions']) > 100:
                self.metrics['transactions'] = self.metrics['transactions'][-100:]

        except Exception as e:
            logger.error(f"Error monitoring transaction: {str(e)}")
            self.metrics['errors'].append({
                'timestamp': timestamp,
                'error': str(e)
            })

    def send_alert(self, message: str) -> None:
        logger.warning(f"Blockchain Alert: {message}")
        # Additional alert channels can be added here (email, Slack, etc.)

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics
