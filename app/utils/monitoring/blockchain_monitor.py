import asyncio
from datetime import datetime, timedelta
import logging
from typing import Dict, List
from web3 import Web3
from app.models import db
from app.models.models import Transaction

logger = logging.getLogger(__name__)

class BlockchainMonitor:
    def __init__(self, web3_provider: str):
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        self.last_block = 0
        self.pending_transactions: Dict[str, datetime] = {}

    async def start_monitoring(self):
        """Start blockchain monitoring process"""
        while True:
            try:
                await self._check_transactions()
                await self._verify_pending_transactions()
                await asyncio.sleep(15)  # Check every 15 seconds
            except Exception as e:
                logger.error(f"Blockchain monitoring error: {str(e)}")
                await asyncio.sleep(30)  # Longer wait on error

    async def _check_transactions(self):
        """Check for new blockchain transactions"""
        current_block = self.w3.eth.block_number
        if current_block <= self.last_block:
            return

        for block_num in range(self.last_block + 1, current_block + 1):
            block = self.w3.eth.get_block(block_num, full_transactions=True)
            for tx in block.transactions:
                await self._process_transaction(tx)

        self.last_block = current_block

    async def _process_transaction(self, tx: Dict):
        """Process individual blockchain transaction"""
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
        except Exception as e:
            logger.error(f"Error processing transaction {tx['hash'].hex()}: {str(e)}")

    async def _verify_pending_transactions(self):
        """Verify status of pending transactions"""
        timeout = datetime.utcnow() - timedelta(minutes=30)
        pending_txs = Transaction.query.filter_by(status='PENDING')\
                                     .filter(Transaction.created_at < timeout)\
                                     .all()

        for tx in pending_txs:
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx.blockchain_tx)
                if receipt:
                    tx.status = 'COMPLETED' if receipt['status'] == 1 else 'FAILED'
                    tx.confirmed_at = datetime.utcnow()
                    db.session.commit()
            except Exception as e:
                logger.error(f"Error verifying transaction {tx.blockchain_tx}: {str(e)}")