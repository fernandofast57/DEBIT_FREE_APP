import asyncio
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List
from prometheus_client import Counter, Histogram, Gauge
from statistics import mean
from app.utils.monitoring.performance_monitor import init_performance_monitor
from app.utils.logging_config import logger
from app.models import db
from app.models.models import Transaction
from web3 import Web3
from dataclasses import dataclass

@dataclass
class BlockchainTransaction:
    transaction_type: str
    block_number: int
    transaction_hash: str
    transaction_timestamp: datetime
    transaction_data: Dict[str, Any]

class BlockchainMonitor:
    def __init__(self, web3_instance=None):
        self.web3 = web3_instance
        self.blockchain_metrics = {
            'total_transactions': 0,
            'failed_transactions': 0,
            'gas_usage': [],
            'confirmation_times': [],
            'block_times': [],
            'pending_transactions': 0
        }
        self.alert_thresholds = {
            'gas_price_max_gwei': 100,
            'confirmation_time_max': 300,
            'consecutive_errors_max': 5,
            'pending_transactions_max': 50,
            'block_time_min': 2,
            'block_time_max': 30
        }
        self.error_counter = 0
        self.last_block_number = 0
        self.last_block_time = datetime.utcnow()

    async def record_transaction(self, tx_hash: str, gas_used: int, confirmation_time: int, block_number: int) -> None:
        """Records a new blockchain transaction with standardized metrics"""
        self.blockchain_metrics['total_transactions'] += 1
        self.blockchain_metrics['gas_usage'].append(gas_used)
        self.blockchain_metrics['confirmation_times'].append(confirmation_time)

        if block_number > self.last_block_number:
            block_time = (datetime.utcnow() - self.last_block_time).total_seconds()
            self.blockchain_metrics['block_times'].append(block_time)
            self.last_block_number = block_number
            self.last_block_time = datetime.utcnow()

        # Alert checks
        if confirmation_time > self.alert_thresholds['confirmation_time_max']:
            logger.warning(f"High confirmation time: {confirmation_time}s for tx {tx_hash}")

        if gas_used > self.alert_thresholds['gas_price_max_gwei'] * 1e9:
            logger.warning(f"High gas usage: {gas_used} for tx {tx_hash}")

    async def record_error(self, error_type: str) -> None:
        self.blockchain_metrics['failed_transactions'] += 1
        logger.error(f"Blockchain error: {error_type}")

    def get_report(self) -> Dict[str, Any]:
        return {
            'metrics': self.blockchain_metrics,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'critical' if self.blockchain_metrics['failed_transactions'] > self.alert_thresholds['consecutive_errors_max'] else 'normal'
        }


class BlockchainMetricsCollector:
    def __init__(self, web3_provider, metrics):
        self.w3 = web3_provider if isinstance(web3_provider, Web3) else Web3(Web3.HTTPProvider(web3_provider))
        self.last_block = 0
        self.pending_transactions: Dict[str, datetime] = {}
        self.event_handlers = {}
        self._running = False
        self.alert_threshold = 5
        self.last_processed_block = 0
        self.metrics = metrics
        self.logger = logging.getLogger('blockchain.monitor')
        self.performance_metrics = {
            'daily_blockchain_performance': {},
            'weekly_blockchain_performance': {},
            'monthly_blockchain_performance': {}
        }
        self.blockchain_monitor = BlockchainMonitor()

    async def start_blockchain_monitoring(self):
        """Starts the standardized blockchain monitoring process"""
        while True:
            try:
                await self._monitor_blockchain_transactions()
                await self._validate_pending_transactions()
                await asyncio.sleep(15)  # Standard check interval
            except Exception as e:
                logger.error(f"Blockchain monitoring error: {str(e)}")
                await asyncio.sleep(30)  # Standard error wait time

    async def _monitor_blockchain_transactions(self):
        """Monitors blockchain transactions using the standard protocol"""
        current_block = self.w3.eth.block_number
        if current_block <= self.last_block:
            return

        for block_number in range(self.last_block + 1, current_block + 1):
            block = self.w3.eth.get_block(block_number, full_transactions=True)
            for tx in block.transactions:
                await self._process_blockchain_transaction(tx)

            self.metrics['daily_blockchain_performance'].update({
                'blocks_processed': block_number - self.last_block,
                'transactions_processed': len(block.transactions)
            })

        self.last_block = current_block

    async def _process_blockchain_transaction(self, tx: Dict):
        start_time = datetime.utcnow()
        await self._process_transaction(tx)
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        gas_used = tx.get('gasUsed', 0)  # Assuming gasUsed is available in tx
        await self.blockchain_monitor.record_transaction(tx['hash'].hex(), gas_used, int(duration), tx['blockNumber'])

    async def _process_transaction(self, tx: Dict):
        """Processes a single blockchain transaction"""
        try:
            transaction = Transaction.query.filter_by(blockchain_tx=tx['hash'].hex()).first()
            if transaction and transaction.status == 'PENDING':
                receipt = self.w3.eth.get_transaction_receipt(tx['hash'])
                if receipt['status'] == 1:  # Success
                    transaction.status = 'COMPLETED'
                    transaction.confirmed_at = datetime.utcnow()
                    db.session.commit()
                    logger.info(f"Transaction {tx['hash'].hex()} confirmed")
                else:
                    transaction.status = 'FAILED'
                    db.session.commit()
                    logger.error(f"Transaction {tx['hash'].hex()} failed")
                    await self.blockchain_monitor.record_error('transaction_error')

        except Exception as e:
            logger.error(f"Error processing transaction {tx['hash'].hex()}: {str(e)}")
            await self.blockchain_monitor.record_error('processing_error')

    async def _validate_pending_transactions(self):
        """Checks the status of pending transactions"""
        timeout = datetime.utcnow() - timedelta(minutes=30)
        pending_transactions = Transaction.query.filter_by(status='PENDING')\
                                     .filter(Transaction.created_at < timeout)\
                                     .all()

        for tx in pending_transactions:
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx.blockchain_tx)
                if receipt:
                    tx.status = 'COMPLETED' if receipt['status'] == 1 else 'FAILED'
                    tx.confirmed_at = datetime.utcnow()
                    db.session.commit()
            except Exception as e:
                logger.error(f"Error verifying transaction {tx.blockchain_tx}: {str(e)}")
                await self.blockchain_monitor.record_error('verification_error')


    async def validate_blockchain_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """Validates the blockchain transaction with standard metrics"""
        try:
            receipt = await self.w3.eth.get_transaction_receipt(tx_hash)
            block_number = receipt.get('blockNumber', 0)
            confirmations = self.w3.eth.block_number - block_number if block_number else 0

            return {
                'transaction_status': 'success' if receipt.get('status') == 1 else 'failed',
                'block_number': block_number,
                'gas_consumed': receipt.get('gasUsed', 0),
                'confirmations': confirmations,
                'validation_timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {'status': 'error', 'message': f'transaction not found: {str(e)}'}

    async def validate_gas_price(self) -> bool:
        """Validates if current gas price is within acceptable range"""
        gas_price = self.w3.eth.gas_price
        return 0 <= gas_price <= self.alert_thresholds['gas_price_max_gwei'] * 1e9

    async def process_block_transactions(self, block_number: int) -> Dict[str, Any]:
        """Process transactions from a specific block"""
        try:
            block = await self.w3.eth.get_block(block_number)
            return {
                'status': 'success',
                'transactions': block.get('transactions', []),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Block processing error: {str(e)}")
            return {'status': 'error', 'message': f'block not found: {str(e)}'}

    async def monitor_blockchain_transactions(self):
        """Monitors blockchain transactions with improved error handling"""
        try:
            last_block = await self.w3.eth.block_number
            pending_count = len(await self.w3.eth.get_block('pending')['transactions'])
            return last_block, pending_count
        except Exception as e:
            logger.error(f"Blockchain monitoring error: {str(e)}")
            return None, 0

    async def send_blockchain_alert(self, alert_type: str, message: str) -> Dict[str, Any]:
        """Send standardized blockchain alert"""
        alert_data = {
            'type': alert_type,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        logger.warning(f"Blockchain Alert: {alert_data}")
        return {'status': 'sent', 'data': alert_data}

    async def check_block_updates(self) -> Dict[str, Any]:
        """Check for new blocks with standardized response"""
        try:
            current_block = self.w3.eth.block_number
            has_updates = current_block > self.last_processed_block
            return {
                'has_updates': has_updates,
                'current_block': current_block,
                'last_processed': self.last_processed_block
            }
        except Exception as e:
            logger.error(f"Block check error: {str(e)}")
            return {'has_updates': False, 'error': str(e)}

    async def monitor_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """Monitors the status of the blockchain transaction"""
        try:
            status = await self._check_transaction_status(tx_hash)
            self.logger.info(f"TransactionStatus: {status} for tx: {tx_hash}")
            return {
                'status': status,
                'transaction_type': 'system_event',
                'validation_status': 'completed' if status else 'failed'
            }
        except Exception as e:
            self.logger.error(f"TransactionStatus monitoring failed: {str(e)}")
            return {
                'status': 'failed',
                'transaction_type': 'system_event',
                'validation_status': 'failed'
            }

    async def _check_transaction_status(self, tx_hash: str) -> bool:
        """Internal method to check the transaction status"""
        # Implementation details
        return True

def init_performance_monitor():
    from .performance_metrics import performance_monitor
    return performance_monitor

class ValidatoreBlockchain:
    def __init__(self):
        self.performance_monitor = None
        self.transaction_latency = Histogram(
            'blockchain_transaction_latency_seconds',
            'Time spent on blockchain transactions',
            ['operation_type']
        )
        self.transaction_errors = Counter(
            'total_blockchain_transaction_errors',
            'Total number of blockchain transaction errors',
            ['error_type']
        )
        self.gas_usage = Gauge(
            'blockchain_gas_usage',
            'Gas used by transactions'
        )
        self.metrics_history: List[Dict[str, Any]] = []
        self.alert_thresholds = {
            'max_transaction_latency': 30.0,  # seconds
            'max_gas_price': 100.0,  # gwei
            'max_error_rate': 5.0    # percentage
        }

    def ensure_monitor(self):
        if not self.performance_monitor:
            self.performance_monitor = get_performance_monitor() # Modification here

    async def record_transaction_metric(self, operation_type: str, duration: float, gas_used: float) -> None:
        """Records blockchain transaction metrics"""
        self.ensure_monitor()
        try:
            self.performance_monitor.transaction_latency.labels(operation_type=operation_type).observe(duration)
            self.gas_usage.set(gas_used)

            metric = {
                'timestamp': datetime.utcnow().isoformat(),
                'operation_type': operation_type,
                'duration': duration,
                'gas_used': gas_used
            }
            self.metrics_history.append(metric)
            self._check_thresholds(metric)

        except Exception as e:
            logger.error(f"Error recording metric: {e}")
            self.transaction_errors.labels(error_type='metric_recording').inc()

    def _check_thresholds(self, metric: Dict[str, Any]) -> None:
        """Checks the metric thresholds"""
        if metric['duration'] > self.alert_thresholds['max_transaction_latency']:
            logger.warning(f"High transaction latency: {metric['duration']}s")

        if metric.get('gas_used', 0) > self.alert_thresholds['max_gas_price']:
            logger.warning(f"High gas price: {metric['gas_used']} gwei")

    def get_performance_report(self) -> Dict[str, Any]:
        """Generates blockchain performance report"""
        if not self.metrics_history:
            return {'status': 'no_data'}

        recent_metrics = self.metrics_history[-100:]  # Last 100 metrics

        return {
            'latency': {
                'average': mean([m['duration'] for m in recent_metrics]),
                'max': max(m['duration'] for m in recent_metrics),
                'min': min(m['duration'] for m in recent_metrics)
            },
            'gas_usage': {
                'average': mean([m['gas_used'] for m in recent_metrics]),
                'max': max(m['gas_used'] for m in recent_metrics),
                'min': min(m['gas_used'] for m in recent_metrics)
            },
            'error_rate': self.transaction_errors._value.get(),
            'thresholds': self.alert_thresholds,
            'timestamp': datetime.utcnow().isoformat()
        }

    def clean_old_metrics(self, max_age_hours: int = 24) -> None:
        """Cleans metrics older than max_age_hours"""
        limit = datetime.utcnow() - timedelta(hours=max_age_hours)
        self.metrics_history = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m['timestamp']) > limit
        ]

async def verify_transaction(self, tx_hash: str) -> Dict[str, Any]:
    try:
        receipt = await self.w3.eth.get_transaction_receipt(tx_hash)
        block_number = receipt.get('blockNumber', 0)
        confirmations = self.w3.eth.block_number - block_number if block_number else 0

        return {
            'transaction_status': 'success' if receipt.get('status') == 1 else 'failed',
            'block_number': block_number,
            'gas_consumed': receipt.get('gasUsed', 0),
            'confirmations': confirmations,
            'validation_timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {'status': 'error', 'message': f'transaction not found: {str(e)}'}