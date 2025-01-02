
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

class BlockchainMonitor:
    def __init__(self):
        pass

    def monitor_transactions(self, transaction_data):
        pass

    def send_alert(self, message):
        pass

class BlockchainService:
    def __init__(self):
        self.w3 = None
        self.contract = None
        self.account = None
        self.monitor = None
        self.setup_web3()
        if self.w3:
            self.monitor = BlockchainMonitor()
        
    def setup_web3(self):
        self.rpc_endpoints = os.getenv('RPC_ENDPOINTS', '').split(',')
        self.current_rpc_index = 0
        self._connect_to_rpc()
        
    @retry_with_backoff(max_retries=3, initial_delay=1, max_delay=10)
    def _connect_to_rpc(self):
        """Connessione a RPC con retry automatico e rotazione endpoint"""
        if not self.rpc_endpoints:
            raise ValueError("No RPC endpoints configured")
        
        attempts = 0
        while attempts < len(self.rpc_endpoints):
            endpoint = self.rpc_endpoints[self.current_rpc_index].strip()
            try:
                logger.info(f"Tentativo connessione a: {endpoint}")
                self.w3 = Web3(Web3.HTTPProvider(endpoint, request_kwargs={'timeout': 10}))
                self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                
                if self.w3.is_connected():
                    logger.info(f"Connesso con successo al nodo: {endpoint}")
                    self._setup_contract()
                    self._setup_account()
                    return True
                    
            except Exception as e:
                logger.warning(f"Connessione fallita a {endpoint}: {str(e)}")
                self.current_rpc_index = (self.current_rpc_index + 1) % len(self.rpc_endpoints)
                attempts += 1
                
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
            logger.error(f"Contract setup error: {str(e)}")
            raise

    def _setup_account(self):
        private_key = os.getenv('PRIVATE_KEY')
        if not private_key:
            raise ValueError("PRIVATE_KEY not set in environment")
        try:
            self.account = self.w3.eth.account.from_key(private_key)
        except Exception as e:
            logger.error(f"Account setup error: {str(e)}")
            raise
