
from web3 import Web3
from decimal import Decimal
import os
from app.utils.logging_config import logger

class BlockchainService:
    def __init__(self):
        self.rpc_endpoint = os.getenv('RPC_ENDPOINTS').split(',')[0]
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_endpoint))
        self.contract_address = os.getenv('CONTRACT_ADDRESS')
        self.private_key = os.getenv('PRIVATE_KEY')
        
    async def send_transaction(self, function_name: str, *args) -> dict:
        try:
            contract = self.web3.eth.contract(
                address=self.contract_address,
                abi=self.load_contract_abi()
            )
            
            function = getattr(contract.functions, function_name)
            tx = function(*args).build_transaction({
                'from': self.web3.eth.account.from_key(self.private_key).address,
                'nonce': self.web3.eth.get_transaction_count(
                    self.web3.eth.account.from_key(self.private_key).address
                ),
                'gas': 2000000,
                'gasPrice': self.web3.eth.gas_price
            })
            
            signed_tx = self.web3.eth.account.sign_transaction(
                tx, self.private_key
            )
            tx_hash = self.web3.eth.send_raw_transaction(
                signed_tx.rawTransaction
            )
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'status': 'success',
                'tx_hash': receipt.transactionHash.hex(),
                'block_number': receipt.blockNumber
            }
            
        except Exception as e:
            logger.error(f"Blockchain transaction error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
            
    def load_contract_abi(self):
        try:
            with open('blockchain/contracts/GoldSystem.abi', 'r') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading contract ABI: {str(e)}")
            raise
