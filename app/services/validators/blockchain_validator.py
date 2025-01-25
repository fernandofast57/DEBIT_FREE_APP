from web3 import Web3
from decimal import Decimal
from typing import Dict
from app.utils.logging_config import logger

class BlockchainValidator:
    def __init__(self, web3_provider):
        self.web3 = Web3(Web3.HTTPProvider(web3_provider))

    def validate_transaction(self, tx_hash: str) -> Dict:
        try:
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            block_number = receipt.blockNumber
            confirmations = self.web3.eth.block_number - block_number

            return {
                'valid': receipt.status == 1,
                'status': 'verified' if receipt.status == 1 else 'rejected',
                'confirmations': confirmations,
                'block': block_number,
                'gas_used': receipt.gasUsed
            }
        except Exception as e:
            logger.error(f"Validation error for tx {tx_hash}: {str(e)}")
            return {'valid': False, 'status': 'error', 'message': str(e)}