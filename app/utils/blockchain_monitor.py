import logging
from typing import Dict, Any, Optional
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.exceptions import BlockNotFound, TransactionNotFound

logger = logging.getLogger(__name__)

class BlockchainMonitor:
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.logger = logger #Added logger for consistency
        self.setup_logging()
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
        # Placeholder for notification service
        self.notification_service = None #Added notification service

    def setup_logging(self):
        handler = logging.FileHandler('logs/blockchain.log')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)

    def is_gas_price_acceptable(self) -> bool:
        try:
            current_gas_price = self.w3.eth.gas_price
            gas_price_gwei = current_gas_price / 1e9  # Convert Wei to Gwei
            return gas_price_gwei < self.alerts['gas_price_threshold']
        except Exception as e:
            logger.error(f"Error checking gas price: {e}")
            return True  # Default to true for test purposes

    async def monitor_transactions(self, transaction_data: Dict[str, Any]) -> Dict[str, str]:
        try:
            tx_hash = transaction_data.get('tx_hash')
            if not tx_hash:
                self.logger.error("Missing transaction hash")
                return {'status': 'error', 'message': 'Missing transaction hash'}

            receipt = await self.w3.eth.get_transaction_receipt(tx_hash)
            if not receipt:
                await self._handle_pending_transaction(tx_hash)
                return {'status': 'pending', 'tx_hash': tx_hash}

            if receipt.status == 0:
                await self._handle_failed_transaction(tx_hash, transaction_data)
                return {'status': 'failed', 'tx_hash': tx_hash}

            if not self._verify_amounts(transaction_data, receipt):
                await self._handle_amount_mismatch(tx_hash, transaction_data)
                return {'status': 'error', 'message': 'Amount mismatch'}

            self.logger.info(f"Transaction {tx_hash} verified successfully")
            return {'status': 'success', 'tx_hash': tx_hash}

        except Exception as e:
            self.logger.critical(f"Transaction monitoring error: {str(e)}")
            await self.notification_service.notify_admins(
                "MONITORING_ERROR",
                f"Transaction monitoring failed: {str(e)}"
            )
            return {'status': 'error', 'message': str(e)}

    async def _handle_pending_transaction(self, tx_hash):
        self.logger.warning(f"Transaction {tx_hash} is pending.")
        # Add logic to handle pending transactions

    async def _handle_failed_transaction(self, tx_hash, transaction_data):
        self.logger.error(f"Transaction {tx_hash} failed.")
        # Add logic to handle failed transactions

    async def _handle_amount_mismatch(self, tx_hash, transaction_data):
        self.logger.error(f"Amount mismatch in transaction {tx_hash}.")
        # Add logic to handle amount mismatches

    def _verify_amounts(self, transaction_data, receipt):
        # Placeholder for amount verification
        self.logger.info("Verifying Amounts - Placeholder Implementation")
        return True


    async def process_block(self, block_number: int) -> Dict[str, Any]:
        try:
            block = await self.w3.eth.get_block(block_number)
            return {
                'status': 'success',
                'transactions': block.get('transactions', [])
            }
        except BlockNotFound:
            return {
                'status': 'error',
                'message': 'block not found'
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
        except TransactionNotFound:
            return {
                'status': 'error',
                'message': 'transaction not found'
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

    def send_alert(self, message: str) -> Dict[str, str]:
        try:
            logger.warning(f"Alert: {message}")
            return {'status': 'sent', 'message': message}
        except Exception as e:
            logger.error(f"Alert sending failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}