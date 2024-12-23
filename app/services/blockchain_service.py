from web3 import Web3
from web3.middleware import geth_poa_middleware
import os
import json
import logging
from app.utils.retry import retry_with_backoff
from app.utils.logging_config import get_logger, APP_NAME
from typing import List, Dict

logger = logging.getLogger(APP_NAME)

class BlockchainService:
    def __init__(self):
        self.w3 = None
        self.contract = None
        self.account = None # Added to store the account
        self.setup_web3()
        
    def setup_web3(self):
        self.rpc_endpoints = os.getenv('RPC_ENDPOINTS', '').split(',')
        self.current_rpc_index = 0
        self._connect_to_rpc()
        
    def _connect_to_rpc(self):
        if not self.rpc_endpoints:
            raise ValueError("No RPC endpoints configured")
            
        endpoint = self.rpc_endpoints[self.current_rpc_index].strip()
        try:
            self.w3 = Web3(Web3.HTTPProvider(endpoint))
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            if self.w3.is_connected():
                logger.info(f"Connected to blockchain node: {endpoint}")
                self._setup_contract()
                self._setup_account() # Added to setup account after connection
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to connect to {endpoint}: {str(e)}")
            return self._try_next_rpc()
            
    def _try_next_rpc(self):
        self.current_rpc_index = (self.current_rpc_index + 1) % len(self.rpc_endpoints)
        return self._connect_to_rpc()
                
    def _setup_contract(self):
        contract_address = os.getenv('CONTRACT_ADDRESS')
        if not contract_address:
            raise ValueError("CONTRACT_ADDRESS not set in environment")
            
        try:
            with open('blockchain/contracts/GoldSystem.json') as f:
                contract_json = json.load(f)
            self.contract = self.w3.eth.contract(
                address=contract_address,
                abi=contract_json['abi']
            )
        except Exception as e:
            logger.error(f"Failed to setup contract: {str(e)}")
            raise

    def _setup_account(self):
        private_key = os.getenv('PRIVATE_KEY')
        if not private_key:
            raise ValueError("PRIVATE_KEY not set in environment")
        try:
            self.account = self.w3.eth.account.from_key(private_key)
        except Exception as e:
            logger.error(f"Failed to setup account: {str(e)}")
            raise

    @retry_with_backoff(max_retries=3, initial_delay=1, max_delay=10)
    async def update_noble_rank(self, address: str, rank: int):
        """Update noble rank with enhanced error handling"""
        if not self.w3 or not self.contract or not self.account: #Check account as well
            logger.error("Blockchain connection or account not initialized")
            raise ValueError("Blockchain connection or account not initialized")
            
        try:
            if not self.w3.is_address(address):
                raise ValueError("Invalid Ethereum address")
                
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            transaction = self.contract.functions.updateNobleRank(
                address,
                rank
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction, os.getenv('PRIVATE_KEY') #Use environment variable again for security
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Noble rank update successful for address {address}")
                return {
                    'status': 'verified',
                    'transaction_hash': receipt.transactionHash.hex(),
                    'block_number': receipt.blockNumber
                }
            else:
                logger.error(f"Noble rank update failed for address {address}")
                return {'status': 'rejected', 'message': 'Transaction failed'}
                
        except Exception as e:
            logger.error(f"Error in update_noble_rank: {str(e)}")
            return {'status': 'rejected', 'message': str(e)}

    async def process_batch_transformation(self, batch_data: List[Dict]) -> Any:
        """Process a batch of transformations on blockchain with security validation"""
        try:
            if not self.w3 or not self.contract or not self.account: #Check account as well
                raise ValueError("Blockchain connection or account not initialized")
            
            # Validate transaction data
            for tx in batch_data:
                if not self._validate_transaction_data(tx):
                    raise ValueError(f"Invalid transaction data: {tx}")
                
            # Validate gas price is within limits
            gas_price = await self.w3.eth.gas_price
            max_gas_price = self.w3.to_wei('100', 'gwei')
            if gas_price > max_gas_price:
                raise ValueError(f"Gas price too high: {gas_price}")
                
            # Validate nonce
            nonce = await self.w3.eth.get_transaction_count(self.account.address)
            if not self._validate_nonce(nonce):
                raise ValueError("Invalid nonce")
                
            # Process batch on blockchain with security checks
            tx = await self.contract.functions.processBatchTransformation(
                batch_data
            ).transact({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 2000000,
                'gasPrice': min(gas_price, max_gas_price)
            })
            
            receipt = await self.w3.eth.wait_for_transaction_receipt(tx)
            if receipt.status != 1:
                raise ValueError("Transaction failed")
                
            return receipt
            
        except Exception as e:
            logger.error(f"Blockchain batch processing error: {str(e)}")
            raise
            
    def _validate_transaction_data(self, tx: Dict) -> bool:
        """Validate individual transaction data"""
        required_fields = ['user_id', 'amount', 'timestamp']
        if not all(field in tx for field in required_fields):
            return False
        if tx['amount'] <= 0:
            return False
        if not isinstance(tx['timestamp'], int):
            return False
        return True
        
    def _validate_nonce(self, nonce: int) -> bool:
        """Validate transaction nonce"""
        return isinstance(nonce, int) and nonce >= 0