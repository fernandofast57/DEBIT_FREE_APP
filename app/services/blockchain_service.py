from web3 import Web3
from web3.middleware import geth_poa_middleware
import os
import json
import logging
from typing import Dict, List, Any, Optional
from functools import lru_cache
from app.utils.monitoring.blockchain_monitor import BlockchainMonitor
from app.utils.retry import retry_with_backoff
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

class BlockchainService:
    def __init__(self):
        self.w3: Optional[Web3] = None
        self.contract = None
        self.account = None
        self.monitor = None

    @lru_cache(maxsize=32)
    def _get_contract_abi(self) -> dict:
        try:
            with open('blockchain/contracts/GoldSystem.json') as f:
                return json.load(f)['abi']
        except Exception as e:
            logger.error(f"Failed to load contract ABI: {e}")
            raise

    async def initialize(self) -> None:
        await self._setup_web3()

    async def _setup_web3(self) -> None:
        self.rpc_endpoints = os.getenv('RPC_ENDPOINTS', '').split(',')
        if not self.rpc_endpoints:
            raise ValueError("No RPC endpoints configured")

        await self._connect_to_rpc()
        if self.w3:
            self.monitor = BlockchainMonitor(self.w3)

    @retry_with_backoff(max_retries=3)
    async def _connect_to_rpc(self) -> bool:
        if not self.rpc_endpoints or all(not endpoint.strip() for endpoint in self.rpc_endpoints):
            logger.error("No valid RPC endpoints configured")
            raise ValueError("No valid RPC endpoints configured")

        for endpoint in self.rpc_endpoints:
            endpoint = endpoint.strip()
            if not endpoint:
                continue
                
            try:
                provider = Web3.HTTPProvider(endpoint, 
                    request_kwargs={'timeout': 30})
                self.w3 = Web3(provider)
                self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

                # Test connection with eth_blockNumber
                if self.w3.eth.block_number:
                    self._setup_contract()
                    self._setup_account()
                    logger.info(f"Connected to blockchain node: {endpoint}")
                    return True

            except Exception as e:
                logger.warning(f"Failed to connect to {endpoint}: {e}")
                continue

        raise ConnectionError("Failed to connect to any RPC endpoint - please check your RPC_ENDPOINTS configuration")

    def _setup_contract(self) -> None:
        contract_address = os.getenv('CONTRACT_ADDRESS')
        if not contract_address:
            raise ValueError("CONTRACT_ADDRESS not set")

        try:
            abi = self._get_contract_abi()
            self.contract = self.w3.eth.contract(
                address=contract_address,
                abi=abi
            )
        except Exception as e:
            logger.error(f"Contract setup failed: {e}")
            raise

    def _setup_account(self) -> None:
        private_key = os.getenv('PRIVATE_KEY')
        if not private_key:
            raise ValueError("PRIVATE_KEY not set")

        try:
            self.account = self.w3.eth.account.from_key(private_key)
        except Exception as e:
            logger.error(f"Account setup failed: {e}")
            raise

    @retry_with_backoff(max_retries=3)
    async def send_transaction(self, func_call, value=0):
        if not self.is_connected():
            raise ValueError("Blockchain connection not initialized")

        try:
            gas_price = min(
                self.w3.eth.gas_price,
                self.w3.to_wei('100', 'gwei')
            )

            transaction = func_call.build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 200000,
                'gasPrice': gas_price,
                'value': value
            })

            signed_txn = self.w3.eth.account.sign_transaction(
                transaction, 
                os.getenv('PRIVATE_KEY')
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt.status != 1:
                raise ValueError("Transaction failed")

            return {
                'status': 'verified',
                'transaction_hash': receipt.transactionHash.hex(),
                'block_number': receipt.blockNumber
            }

        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            return {'status': 'error', 'message': str(e)}

    async def update_noble_rank(self, address: str, rank: int):
        if not self.w3.is_address(address):
            raise ValueError("Invalid Ethereum address")

        return await self.send_transaction(
            self.contract.functions.updateNobleRank(address, rank)
        )

    async def record_gold_transaction(self, address: str, euro_amount: float, 
                                    gold_grams: float) -> Dict[str, Any]:
        return await self.send_transaction(
            self.contract.functions.transformGold(
                address,
                int(euro_amount * 100),
                int(gold_grams * 10000)
            )
        )

    def is_connected(self) -> bool:
        return bool(self.w3 and self.w3.is_connected() and 
                   self.account and self.contract)

    async def get_transaction_stats(self) -> Dict[str, Any]:
        if not self.is_connected():
            return {'status': 'error', 'message': 'Not connected'}

        try:
            return {
                'status': 'verified',
                'stats': {
                    'gas_price': self.w3.eth.gas_price,
                    'block_number': self.w3.eth.block_number,
                    'network_id': self.w3.eth.chain_id,
                    'connected': True,
                    'syncing': self.w3.eth.syncing,
                    'peer_count': self.w3.net.peer_count
                }
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {'status': 'error', 'message': str(e)}