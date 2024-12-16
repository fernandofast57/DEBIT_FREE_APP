
from typing import Dict, List, Any
from web3 import Web3
from eth_account import Account
from decimal import Decimal
from app.utils.logging_config import logger

class BlockchainService:
    def __init__(self, web3_provider: str = "http://0.0.0.0:8545"):
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        self.batch = []
        
    async def connect(self):
        try:
            if not self.w3.is_connected():
                raise ConnectionError("Failed to connect to Ethereum node")
            logger.info("Connected to Ethereum node")
            return True
        except Exception as e:
            logger.error(f"Error connecting to Ethereum node: {str(e)}")
            raise

    async def add_to_batch(self, user_address: str, euro_amount: Decimal, 
                          gold_grams: Decimal, fixing_price: Decimal) -> bool:
        try:
            self.batch.append({
                'user_address': user_address,
                'euro_amount': euro_amount,
                'gold_grams': gold_grams,
                'fixing_price': fixing_price
            })
            return True
        except Exception as e:
            logger.error(f"Error adding to batch: {e}")
            return False

    async def process_batch(self) -> Dict[str, Any]:
        if not self.batch:
            return {'status': 'error', 'message': 'Empty batch'}
            
        try:
            await self.connect()
            # Process the batch here
            transaction_hash = '0x123...abc'  # Placeholder
            self.batch = []  # Clear batch after processing
            return {
                'status': 'success',
                'transaction_hash': transaction_hash
            }
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            return {'status': 'error', 'message': str(e)}

    async def get_user_transactions(self, address: str) -> List[Dict]:
        try:
            if not self.w3.is_connected():
                await self.connect()
            
            nonce = self.w3.eth.get_transaction_count(address)
            
            transactions = []
            for i in range(nonce):
                tx = self.w3.eth.get_transaction_by_nonce(address, i)
                if tx:
                    transactions.append({
                        'hash': tx['hash'].hex(),
                        'value': self.w3.from_wei(tx['value'], 'ether'),
                        'from': tx['from'],
                        'to': tx['to']
                    })
            return transactions
        except Exception as e:
            logger.error(f"Error getting user transactions: {str(e)}")
            raise

    async def retry_operation(self, operation):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                return await operation()
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    raise e
                logger.warning(f"Retry {retry_count}/{max_retries} after error: {str(e)}")
