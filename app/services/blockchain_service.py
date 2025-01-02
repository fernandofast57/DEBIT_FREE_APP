from web3 import Web3
from web3.middleware import geth_poa_middleware
import os
import json
import logging
import json
from datetime import datetime
from typing import List, Dict, Any
from app.utils.retry import retry_with_backoff
from app.utils.logging_config import get_logger, APP_NAME

logger = logging.getLogger(APP_NAME)

def log_blockchain_transaction(func):
    async def wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        try:
            result = await func(*args, **kwargs)
            end_time = datetime.utcnow()
            
            log_entry = {
                'transaction_type': func.__name__,
                'timestamp': start_time.isoformat(),
                'duration_ms': (end_time - start_time).total_seconds() * 1000,
                'status': 'success' if result and result.get('status') == 'verified' else 'failed',
                'args': str(args),
                'kwargs': str(kwargs)
            }
            
            if result and 'transaction_hash' in result:
                log_entry['tx_hash'] = result['transaction_hash']
                
            logger.info('Blockchain Transaction', extra={'audit': log_entry})
            return result
        except Exception as e:
            logger.error(f"Blockchain transaction error: {str(e)}")
            logger.error(f'Blockchain Transaction Error: {str(e)}', 
                        extra={'error': str(e), 'function': func.__name__})
            return {'status': 'error', 'message': str(e)}
    return wrapper

class BlockchainMonitor:  # Added BlockchainMonitor class
    def __init__(self):
        pass  # Add monitoring logic here as needed

    def monitor_transactions(self, transaction_data):
        #Implementation for monitoring transactions
        pass

    def send_alert(self, message):
        #Implementation for sending alerts
        pass



class BlockchainService:
    def __init__(self):
        self.w3 = None
        self.contract = None
        self.account = None
        self.monitor = None
        self.setup_web3()
        if self.w3:
            self.monitor = BlockchainMonitor(self.w3)
        
    def setup_web3(self):
        self.rpc_endpoints = os.getenv('RPC_ENDPOINTS', '').split(',')
        self.current_rpc_index = 0
        self._connect_to_rpc()
        
    @retry_with_backoff(max_retries=5, initial_delay=1, max_delay=30)
    def _connect_to_rpc(self):
        """Connessione a RPC con retry automatico e rotazione endpoint"""
        if not self.rpc_endpoints:
            raise ValueError("No RPC endpoints configured")
        
        for _ in range(len(self.rpc_endpoints)):
            endpoint = self.rpc_endpoints[self.current_rpc_index].strip()
            try:
                logger.info(f"Tentativo connessione a: {endpoint}")
                self.w3 = Web3(Web3.HTTPProvider(endpoint, request_kwargs={
                    'timeout': 10,
                    'backoff_factor': 0.5,
                    'retry_count': 3
                }))
                self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                
                if self.w3.is_connected():
                    logger.info(f"Connesso con successo al nodo: {endpoint}")
                    self._setup_contract()
                    self._setup_account()
                    return True
                    
            except Exception as e:
                logger.warning(f"Connessione fallita a {endpoint}: {str(e)}")
                self.current_rpc_index = (self.current_rpc_index + 1) % len(self.rpc_endpoints)
                
        logger.error("Tutti i tentativi di connessione falliti, riavvio del ciclo di retry")
        raise ConnectionError("Impossibile connettersi a nessun endpoint RPC")
            

    def is_connected(self) -> bool:
        """Check if blockchain connection is established and account is initialized"""
        return bool(self.w3 and self.w3.is_connected() and self.account and self.contract)
            

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
            logger.error(f"Blockchain transaction error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
            

    def _setup_account(self):
        private_key = os.getenv('PRIVATE_KEY')
        if not private_key:
            raise ValueError("PRIVATE_KEY not set in environment")
        try:
            self.account = self.w3.eth.account.from_key(private_key)
        except Exception as e:
            logger.error(f"Blockchain transaction error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
            

    @log_blockchain_transaction
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
                self.monitor.monitor_transactions({'type': 'update_noble_rank', 'status': 'success', 'tx_hash': receipt.transactionHash.hex()}) #Added monitoring call
                return {
                    'status': 'verified',
                    'transaction_hash': receipt.transactionHash.hex(),
                    'block_number': receipt.blockNumber
                }
            else:
                logger.error(f"Noble rank update failed for address {address}")
                self.monitor.monitor_transactions({'type': 'update_noble_rank', 'status': 'failed', 'tx_hash': receipt.transactionHash.hex()}) #Added monitoring call
                return {'status': 'rejected', 'message': 'Transaction failed'}
                
        except Exception as e:
            logger.error(f"Blockchain transaction error: {str(e)}")
            logger.error(f"Error in update_noble_rank: {str(e)}")
            self.monitor.send_alert(f"Error in update_noble_rank: {str(e)}") #Added alert call
            return {'status': 'rejected', 'message': str(e)}

    @log_blockchain_transaction
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
                
            self.monitor.monitor_transactions({'type': 'process_batch_transformation', 'status': 'success', 'tx_hash': receipt.transactionHash.hex()}) #Added monitoring call
            return receipt
            
        except Exception as e:
            logger.error(f"Blockchain transaction error: {str(e)}")
            logger.error(f"Blockchain batch processing error: {str(e)}")
            self.monitor.send_alert(f"Blockchain batch processing error: {str(e)}") #Added alert call
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
    async def get_transaction_stats(self) -> Dict[str, Any]:
        """Get statistics about blockchain transactions"""
        try:
            if not self.w3:
                return {'status': 'error', 'message': 'Web3 not initialized'}
            
            if not self.w3.is_connected():
                return {'status': 'error', 'message': 'Not connected to blockchain'}

            stats = {
                'gas_price': self.w3.eth.gas_price,
                'block_number': self.w3.eth.block_number,
                'network_id': self.w3.eth.chain_id,
                'connected': True,
                'syncing': self.w3.eth.syncing,
                'peer_count': self.w3.net.peer_count
            }
            return {'status': 'verified', 'stats': stats}
        except Exception as e:
            logger.error(f"Error getting transaction stats: {str(e)}")
            return {'status': 'error', 'message': str(e)}