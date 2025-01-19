from typing import Dict, List, Optional, Any
from web3 import Web3
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging
from app.utils.logging_config import get_logger
from app.utils.retry import retry_with_backoff

logger = get_logger(__name__)

@dataclass
class BlockchainEvent:
    event_type: str
    block_number: int
    transaction_hash: str
    timestamp: datetime
    data: Dict[str, Any]

class BlockchainMonitor:
    def __init__(self, web3_instance: Web3):
        self.w3 = web3_instance
        self.last_processed_block = self._get_last_block()
        self.event_filters = {}
        self.event_handlers = {}
        self._running = False
        self.alert_threshold = 1000000000  # 1 GWEI threshold for extreme gas prices

    def can_process_transactions(self, transactions: list) -> bool:
        return len(transactions) > 0 and all(isinstance(tx, str) for tx in transactions)

    async def process_block(self, block_number: int) -> dict:
        try:
            block = await self.w3.eth.get_block(block_number)
            return {
                'status': 'success',
                'transactions': block.get('transactions', []),
                'number': block_number
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def is_gas_price_acceptable(self) -> bool:
        return 0 <= self.w3.eth.gas_price <= self.alert_threshold

    def monitor_transactions(self, tx_data: dict) -> dict:
        return {'status': 'monitored', 'data': tx_data}

    def send_alert(self, message: str) -> dict:
        return {'status': 'sent', 'message': message}

    def check_new_blocks(self) -> bool:
        try:
            current_block = self.w3.eth.get_block_number()
            return current_block > self.last_processed_block
        except Exception:
            return False

    def _get_last_block(self) -> int:
        try:
            return self.w3.eth.block_number
        except Exception as e:
            logger.error(f"Failed to get last block: {e}")
            return 0

    @retry_with_backoff(max_retries=3)
    async def get_block_details(self, block_number: int) -> Dict[str, Any]:
        """Fetch detailed block information with retry mechanism"""
        try:
            block = await self.w3.eth.get_block(block_number)
            return {
                'status': 'success',
                'block': block
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    async def monitor_events(self, contract_address: str, event_abi: dict):
        """Monitor specific contract events"""
        try:
            event_filter = self.w3.eth.contract(
                address=contract_address,
                abi=[event_abi]
            ).events[event_abi['name']]()

            self.event_filters[event_abi['name']] = event_filter
            return True
        except Exception as e:
            logger.error(f"Failed to create event filter: {e}")
            return False

    async def process_new_blocks(self):
        """Process new blocks and their events"""
        self._running = True
        while self._running:
            try:
                current_block = self.w3.eth.block_number
                if current_block > self.last_processed_block:
                    block_range = range(self.last_processed_block + 1, current_block + 1)

                    for block_num in block_range:
                        block_details = await self.get_block_details(block_num)
                        await self._process_block_events(block_num, block_details)

                    self.last_processed_block = current_block

                await asyncio.sleep(1)  # Polling interval

            except Exception as e:
                logger.error(f"Error in block processing: {e}")
                await asyncio.sleep(5)  # Backoff on error

    async def _process_block_events(self, block_number: int, block_details: Dict[str, Any]):
        """Process events in a specific block"""
        try:
            for event_name, event_filter in self.event_filters.items():
                events = event_filter.get_new_entries()

                for event in events:
                    blockchain_event = BlockchainEvent(
                        event_type=event_name,
                        block_number=block_number,
                        transaction_hash=event.transactionHash.hex(),
                        timestamp=block_details['timestamp'],
                        data=dict(event.args)
                    )

                    if event_name in self.event_handlers:
                        await self.event_handlers[event_name](blockchain_event)

        except Exception as e:
            logger.error(f"Error processing events for block {block_number}: {e}")

    def register_event_handler(self, event_name: str, handler_func):
        """Register a handler function for specific events"""
        self.event_handlers[event_name] = handler_func

    def stop_monitoring(self):
        """Stop the monitoring process"""
        self._running = False

    async def get_network_stats(self) -> Dict[str, Any]:
        """Get current network statistics"""
        try:
            return {
                'latest_block': self.last_processed_block,
                'network_id': await self.w3.eth.chain_id,
                'gas_price': await self.w3.eth.gas_price,
                'is_syncing': await self.w3.eth.syncing,
                'peer_count': await self.w3.net.peer_count,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting network stats: {e}")
            return {}

    async def verify_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Verify transaction status and details"""
        try:
            tx_receipt = await self.w3.eth.get_transaction_receipt(tx_hash)
            if tx_receipt:
                return {
                    'status': 'success' if tx_receipt.status == 1 else 'failed',
                    'block_number': tx_receipt.blockNumber,
                    'gas_used': tx_receipt.gasUsed,
                    'confirmations': self.last_processed_block - tx_receipt.blockNumber
                }
            return None
        except Exception as e:
            logger.error(f"Error verifying transaction {tx_hash}: {e}")
            return None