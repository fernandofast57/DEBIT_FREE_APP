
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from web3 import Web3
from web3.exceptions import BlockNotFound, TransactionNotFound
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

class BlockchainMonitor:
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.metrics = {
            'transactions': [],
            'gas_prices': [],
            'block_times': [],
            'network_stats': {},
            'errors': [],
            'performance_metrics': {
                'avg_block_time': 0,
                'avg_gas_price': 0,
                'transaction_success_rate': 100
            }
        }
        self.alerts = {
            'gas_price_threshold': 100,  # in gwei
            'block_time_threshold': 30,  # in seconds
            'error_threshold': 5,  # max errors before alert
            'low_peer_threshold': 2
        }
        self.last_refresh = datetime.utcnow()
        
    async def monitor_transactions(self, transaction_data: Dict[str, Any]) -> None:
        """Monitor transaction metrics and trigger alerts if needed."""
        try:
            timestamp = datetime.utcnow().isoformat()
            gas_price = await self.w3.eth.gas_price
            
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
            
            # Gas price alert check
            gas_price_gwei = self.w3.from_wei(gas_price, 'gwei')
            if gas_price_gwei > self.alerts['gas_price_threshold']:
                self.send_alert(f"High gas price detected: {gas_price_gwei} gwei")
            
            # Maintain data retention policy
            self._apply_retention_policy()
            
        except Exception as e:
            self._handle_error(f"Transaction monitoring error: {str(e)}")

    async def monitor_block_time(self) -> None:
        """Monitor block times and network performance."""
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
            
            self._update_performance_metrics()
            
            if block_time > self.alerts['block_time_threshold']:
                self.send_alert(f"High block time detected: {block_time} seconds")
                
        except Exception as e:
            self._handle_error(f"Block time monitoring error: {str(e)}")

    async def monitor_network(self) -> None:
        """Monitor network health and connectivity."""
        try:
            network_stats = {
                'peer_count': await self.w3.net.peer_count,
                'is_listening': await self.w3.net.listening,
                'network_id': await self.w3.eth.chain_id,
                'latest_block': await self.w3.eth.block_number,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.metrics['network_stats'] = network_stats
            
            if network_stats['peer_count'] < self.alerts['low_peer_threshold']:
                self.send_alert(f"Low peer count detected: {network_stats['peer_count']}")
                
        except Exception as e:
            self._handle_error(f"Network monitoring error: {str(e)}")

    def _update_performance_metrics(self) -> None:
        """Update aggregate performance metrics."""
        try:
            if self.metrics['block_times']:
                recent_blocks = self.metrics['block_times'][-10:]  # Last 10 blocks
                self.metrics['performance_metrics']['avg_block_time'] = sum(
                    block['block_time'] for block in recent_blocks
                ) / len(recent_blocks)
            
            if self.metrics['gas_prices']:
                recent_gas = self.metrics['gas_prices'][-10:]  # Last 10 gas prices
                self.metrics['performance_metrics']['avg_gas_price'] = sum(
                    recent_gas
                ) / len(recent_gas)
            
            if self.metrics['transactions']:
                recent_txs = self.metrics['transactions'][-100:]
                success_count = sum(
                    1 for tx in recent_txs if tx['status'] == 'success'
                )
                self.metrics['performance_metrics']['transaction_success_rate'] = \
                    (success_count / len(recent_txs)) * 100
                    
        except Exception as e:
            logger.error(f"Error updating performance metrics: {str(e)}")

    def _apply_retention_policy(self) -> None:
        """Apply data retention policies to metrics."""
        max_items = 100
        self.metrics['transactions'] = self.metrics['transactions'][-max_items:]
        self.metrics['gas_prices'] = self.metrics['gas_prices'][-max_items:]
        self.metrics['block_times'] = self.metrics['block_times'][-max_items:]
        self.metrics['errors'] = self.metrics['errors'][-max_items:]

    def _handle_error(self, error_msg: str) -> None:
        """Handle and log errors, trigger alerts if threshold exceeded."""
        timestamp = datetime.utcnow().isoformat()
        self.metrics['errors'].append({
            'timestamp': timestamp,
            'error': error_msg
        })
        
        logger.error(error_msg)
        
        recent_errors = [e for e in self.metrics['errors'] 
                        if datetime.fromisoformat(e['timestamp']) > 
                        datetime.utcnow() - timedelta(hours=1)]
                        
        if len(recent_errors) >= self.alerts['error_threshold']:
            self.send_alert(f"Error threshold exceeded: {len(recent_errors)} errors in the last hour")

    def send_alert(self, message: str) -> None:
        """Send alerts through configured channels."""
        logger.warning(f"Blockchain Alert: {message}")
        # Additional alert channels can be implemented here (email, Slack, etc.)

    def get_metrics(self) -> Dict[str, Any]:
        """Get current monitoring metrics."""
        return self.metrics

    async def get_health_status(self) -> Dict[str, Any]:
        """Get overall blockchain system health status."""
        try:
            is_syncing = await self.w3.eth.syncing
            latest_block = await self.w3.eth.block_number
            
            return {
                'status': 'healthy' if not is_syncing else 'syncing',
                'latest_block': latest_block,
                'performance_metrics': self.metrics['performance_metrics'],
                'network_stats': self.metrics['network_stats'],
                'last_updated': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting health status: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
