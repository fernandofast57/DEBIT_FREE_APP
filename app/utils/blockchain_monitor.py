
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from web3 import Web3

logger = logging.getLogger(__name__)

class BlockchainMonitor:
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.metrics = {
            'transactions': [],
            'gas_prices': [],
            'block_times': [],
            'network_stats': {},
            'errors': []
        }
        self.alerts = {
            'gas_price_threshold': 100,
            'block_time_threshold': 30,
            'error_threshold': 5,
            'low_peer_threshold': 2
        }
        
    def monitor_transactions(self, transaction_data: Dict[str, Any]) -> None:
        """Monitor transaction metrics and trigger alerts if needed."""
        try:
            timestamp = datetime.utcnow().isoformat()
            gas_price = self.w3.eth.gas_price
            
            transaction_info = {
                'timestamp': timestamp,
                'type': transaction_data.get('type', 'unknown'),
                'status': transaction_data.get('status', 'unknown'),
                'tx_hash': transaction_data.get('tx_hash', ''),
                'gas_price': gas_price,
                'block_number': transaction_data.get('block_number')
            }
            
            self.metrics['transactions'].append(transaction_info)
            self.metrics['gas_prices'].append(gas_price)
            
            gas_price_gwei = self.w3.from_wei(gas_price, 'gwei')
            if gas_price_gwei > self.alerts['gas_price_threshold']:
                self.send_alert(f"High gas price detected: {gas_price_gwei} gwei")
            
        except Exception as e:
            logger.error(f"Transaction monitoring error: {str(e)}")

    def send_alert(self, message: str) -> None:
        logger.warning(f"Blockchain Alert: {message}")

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics
