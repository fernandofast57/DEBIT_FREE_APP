
from web3 import Web3
from web3.middleware import geth_poa_middleware
import os
import json
from app.utils.retry import retry_with_backoff
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

class BlockchainService:
    def __init__(self):
        self.w3 = None
        self.contract = None
        self.setup_web3()
        
    def setup_web3(self):
        rpc_endpoints = os.getenv('RPC_ENDPOINTS', '').split(',')
        for endpoint in rpc_endpoints:
            try:
                self.w3 = Web3(Web3.HTTPProvider(endpoint.strip()))
                self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                if self.w3.is_connected():
                    logger.info(f"Connected to blockchain node: {endpoint}")
                    self._setup_contract()
                    break
            except Exception as e:
                logger.error(f"Failed to connect to {endpoint}: {str(e)}")
                continue
                
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

    @retry_with_backoff(max_retries=3)
    async def update_noble_rank(self, address: str, rank: int):
        logger = get_logger(__name__)
        if not self.w3 or not self.contract:
            logger.error("Blockchain connection not initialized")
            raise ValueError("Blockchain connection not initialized")
        try:
            if not self.w3.is_address(address):
                raise ValueError("Invalid Ethereum address")
            
        private_key = os.getenv('PRIVATE_KEY')
        account = self.w3.eth.account.from_key(private_key)
        
        nonce = self.w3.eth.get_transaction_count(account.address)
        
        transaction = self.contract.functions.updateNobleRank(
            address,
            rank
        ).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        signed_txn = self.w3.eth.account.sign_transaction(
            transaction, private_key
        )
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return receipt
