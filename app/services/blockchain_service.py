
from typing import Dict, List
from web3 import Web3
from eth_account import Account
from app.utils.logging_config import logger

class BlockchainService:
    def __init__(self, web3_provider: str = "http://localhost:8545"):
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        
    async def connect(self):
        try:
            if not self.w3.is_connected():
                raise ConnectionError("Failed to connect to Ethereum node")
            logger.info("Connected to Ethereum node")
            return True
        except Exception as e:
            logger.error(f"Error connecting to Ethereum node: {str(e)}")
            raise

    async def get_user_transactions(self, address: str) -> List[Dict]:
        try:
            if not self.w3.is_connected():
                await self.connect()
            
            # Get transaction count
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
