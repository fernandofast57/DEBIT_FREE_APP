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
from app.utils.monitoring.monitoring_manager import get_performance_monitor

logger = get_logger(__name__)

class BlockchainService:
    def __init__(self):
        self.web3_client = None
        self.noble_contract = None
        self.initialization_status = False
        self.monitor = None
        self.logger = logging.getLogger(__name__)
        self._performance_monitor = None

    @property
    def performance_monitor(self):
        if self._performance_monitor is None:
            from app.utils.monitoring.monitoring_manager import get_performance_monitor
            self._performance_monitor = get_performance_monitor()
        return self._performance_monitor

    @lru_cache(maxsize=32)
    def _get_contract_abi(self) -> dict:
        try:
            with open('blockchain/contracts/GoldSystem.json') as f:
                return json.load(f)['abi']
        except Exception as e:
            self.logger.error(f"Failed to load contract ABI: {e}")
            raise

    async def initialize(self) -> None:
        await self._setup_web3()

    async def initialize_web3(self) -> None:
        if os.getenv('BLOCKCHAIN_MODE', 'offline') == 'offline':
            from app.services.mock_blockchain_service import MockBlockchainService
            mock_service = MockBlockchainService()
            self.web3_client = mock_service.w3
            self.noble_contract = mock_service.contract
            self.account = mock_service.account
            self.initialization_status = True
            return

        self.rpc_endpoints = os.getenv('RPC_ENDPOINTS', '').split(',')
        await self._connect_to_rpc()

    @retry_with_backoff(max_retries=3)
    async def _connect_to_rpc(self) -> bool:
        if not self.rpc_endpoints:
            self.logger.error("No valid RPC endpoints configured")
            raise ValueError("Missing or invalid RPC configuration")

        for endpoint in self.rpc_endpoints:
            endpoint = endpoint.strip()
            if not endpoint:
                continue

            try:
                self.logger.info(f"Attempting connection to: {endpoint}")
                provider = Web3.HTTPProvider(endpoint, request_kwargs={
                    'timeout': 60, 
                    'verify': True
                })
                self.web3_client = Web3(provider)
                self.web3_client.middleware_onion.inject(geth_poa_middleware, layer=0)

                if self.web3_client.eth.block_number:
                    self._setup_contract()
                    self._setup_account()
                    self.logger.info(f"Connected to blockchain node: {endpoint}")
                    return True

            except Exception as e:
                self.logger.warning(f"Connection failed to {endpoint}: {e}")
                continue

        raise ConnectionError("Failed to connect to all RPC endpoints")

    def _setup_contract(self) -> None:
        contract_address = os.getenv('CONTRACT_ADDRESS')
        if not contract_address:
            raise ValueError("CONTRACT_ADDRESS not set")

        try:
            abi = self._get_contract_abi()
            self.noble_contract = self.web3_client.eth.contract(
                address=contract_address,
                abi=abi
            )
        except Exception as e:
            self.logger.error(f"Contract setup failed: {e}")
            raise

    def _setup_account(self) -> None:
        private_key = os.getenv('PRIVATE_KEY')
        if not private_key:
            raise ValueError("PRIVATE_KEY not set")

        try:
            self.account = self.web3_client.eth.account.from_key(private_key)
        except Exception as e:
            self.logger.error(f"Account setup failed: {e}")
            raise

    @retry_with_backoff(max_retries=3)
    async def send_transaction(self, func_call, value=0):
        if not self.is_connected():
            raise ValueError("Blockchain connection not initialized")

        try:
            gas_price = min(
                self.web3_client.eth.gas_price,
                self.web3_client.to_wei('100', 'gwei')
            )

            transaction = func_call.build_transaction({
                'from': self.account.address,
                'nonce': self.web3_client.eth.get_transaction_count(self.account.address),
                'gas': 200000,
                'gasPrice': gas_price,
                'value': value
            })

            signed_txn = self.web3_client.eth.account.sign_transaction(
                transaction, 
                os.getenv('PRIVATE_KEY')
            )
            tx_hash = self.web3_client.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.web3_client.eth.wait_for_transaction_receipt(tx_hash)

            if receipt.status != 1:
                raise ValueError("Transaction failed")

            return {
                'status': 'completed',
                'transaction_hash': receipt.transactionHash.hex(),
                'block_number': receipt.blockNumber
            }

        except Exception as e:
            self.logger.error(f"Transaction failed: {e}")
            return {'status': 'error', 'message': str(e)}

    def is_connected(self) -> bool:
        return bool(self.web3_client and self.web3_client.is_connected() and 
                   self.account and self.noble_contract)

    async def get_transaction_stats(self) -> Dict[str, Any]:
        if not self.is_connected():
            return {'status': 'error', 'message': 'Not connected'}

        try:
            return {
                'status': 'verified',
                'stats': {
                    'gas_price': self.web3_client.eth.gas_price,
                    'block_number': self.web3_client.eth.block_number,
                    'network_id': self.web3_client.eth.chain_id,
                    'connected': True,
                    'syncing': self.web3_client.eth.syncing,
                    'peer_count': self.web3_client.net.peer_count
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            return {'status': 'error', 'message': str(e)}

    async def update_noble_rank(self, address: str, rank: int):
        if not self.web3_client.is_address(address):
            raise ValueError("Invalid Ethereum address")

        self.performance_monitor.start_timer('update_noble_rank')
        result = await self.send_transaction(
            self.noble_contract.functions.updateNobleRank(address, rank)
        )
        self.performance_monitor.stop_timer('update_noble_rank')
        return result

    async def record_gold_transaction(self, address: str, euro_amount: float, 
                                    gold_grams: float, validation_status: str = None) -> Dict[str, Any]:
        if not validation_status or validation_status != 'approved':
            self.logger.error("Transaction not approved by administrator")
            return {'status': 'error', 'message': 'Transaction requires approval before blockchain recording'}

        self.performance_monitor.start_timer('record_gold_transaction')
        result = await self.send_transaction(
            self.noble_contract.functions.transformGold(
                address,
                int(euro_amount * 100),
                int(gold_grams * 10000)
            )
        )
        self.performance_monitor.stop_timer('record_gold_transaction')
        return result