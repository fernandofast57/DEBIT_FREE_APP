
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

    async def monitor_block_time(self) -> None:
        try:
            current_block = await self.w3.eth.block_number
            block = await self.w3.eth.get_block(current_block)
            prev_block = await self.w3.eth.get_block(current_block - 1)
            
            block_time = block.timestamp - prev_block.timestamp
            
            self.metrics['block_times'].append({
                'block_number': current_block,
                'block_time': block_time,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            if block_time > self.alerts['block_time_threshold']:
                self.send_alert(f"High block time detected: {block_time} seconds")
                
            # Keep only last 100 block times
            if len(self.metrics['block_times']) > 100:
                self.metrics['block_times'] = self.metrics['block_times'][-100:]
                
        except Exception as e:
            logger.error(f"Error monitoring block time: {str(e)}")
            
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

    async def monitor_network(self) -> None:
        try:
            network_stats = {
                'peer_count': await self.w3.net.peer_count,
                'is_listening': await self.w3.net.listening,
                'network_id': await self.w3.eth.chain_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.metrics['network_stats'] = network_stats
            
            if network_stats['peer_count'] < 2:
                self.send_alert("Low peer count detected")
                
        except Exception as e:
            logger.error(f"Error monitoring network: {str(e)}")
            
    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics
