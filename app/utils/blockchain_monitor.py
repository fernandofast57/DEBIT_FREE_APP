
import asyncio
from datetime import datetime
from typing import Dict, Any
import logging
from web3 import Web3
from web3.exceptions import BlockNotFound

logger = logging.getLogger(__name__)

class BlockchainMonitor:
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.metrics = {
            'latest_block': 0,
            'gas_price': 0,
            'pending_transactions': 0,
            'network_status': 'unknown'
        }
        self.thresholds = {
            'max_gas_price': 100_000_000_000,  # 100 gwei
            'block_delay': 5,  # blocks
            'min_peers': 2
        }

    async def monitor_network(self) -> Dict[str, Any]:
        try:
            latest_block = await self.w3.eth.block_number
            gas_price = await self.w3.eth.gas_price
            peers = await self.w3.net.peer_count

            self.metrics.update({
                'latest_block': latest_block,
                'gas_price': gas_price,
                'network_status': 'healthy' if peers >= self.thresholds['min_peers'] else 'warning',
                'timestamp': datetime.utcnow().isoformat()
            })

            # Alert on high gas prices
            if gas_price > self.thresholds['max_gas_price']:
                logger.warning(f"High gas price detected: {gas_price}")

            return self.metrics

        except Exception as e:
            logger.error(f"Blockchain monitoring error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def verify_transaction(self, tx_hash: str) -> bool:
        try:
            tx = await self.w3.eth.get_transaction(tx_hash)
            if tx is None:
                return False
            return tx.blockNumber is not None
        except Exception:
            return False
