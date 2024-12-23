
import logging
from datetime import datetime
from typing import Dict, Any
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

class BlockchainMonitor:
    def __init__(self):
        self.error_thresholds = {
            'gas_price_max': 100_000_000_000,  # 100 gwei
            'failed_tx_limit': 3,
            'block_delay_limit': 10
        }
        self.failed_transactions = 0
        self.last_block = 0
        
    async def check_network_health(self, w3) -> Dict[str, Any]:
        try:
            current_block = await w3.eth.block_number
            gas_price = await w3.eth.gas_price
            peers = await w3.net.peer_count
            
            health_status = {
                'status': 'healthy',
                'gas_price': gas_price,
                'block_number': current_block,
                'peer_count': peers,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if gas_price > self.error_thresholds['gas_price_max']:
                health_status['status'] = 'warning'
                health_status['warning'] = 'High gas price detected'
                
            if peers < 2:
                health_status['status'] = 'warning'
                health_status['warning'] = 'Low peer count'
                
            return health_status
            
        except Exception as e:
            logger.error(f"Network health check failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
            
    def track_transaction_failure(self):
        self.failed_transactions += 1
        if self.failed_transactions >= self.error_thresholds['failed_tx_limit']:
            logger.critical("Transaction failure threshold exceeded")
            return False
        return True
        
    def reset_failure_count(self):
        self.failed_transactions = 0
