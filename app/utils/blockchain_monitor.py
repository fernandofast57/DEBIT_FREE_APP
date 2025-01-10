import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from web3 import Web3

logger = logging.getLogger(__name__)

class BlockchainMonitor:
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.latest_block = None
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

    async def monitor_transactions(self):
        try:
            latest_block = await self.w3.eth.get_block('latest')
            self.latest_block = latest_block
            return latest_block
        except Exception as e:
            return None

    def send_alert(self, message: str) -> None:
        logger.warning(f"Blockchain Alert: {message}")

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics