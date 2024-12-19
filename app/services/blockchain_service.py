# app/services/blockchain_service.py

from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import logging
from typing import List, Dict
import asyncio
from ..utils.retry import retry_with_fallback
from ..models.models import GoldTransformation
import os
# Assuming db is defined elsewhere, adjust as needed
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

logger = logging.getLogger(__name__)

class BlockchainService:
    def __init__(self):
        self.rpc_endpoints = [
            "https://rpc-mumbai.maticvigil.com",
            "https://matic-mumbai.chainstacklabs.com",
            "https://matic-testnet-archive-rpc.bwarelabs.com"
        ]
        self.current_rpc_index = 0
        self.web3 = self._initialize_web3()
        self.contract = self._initialize_contract()
        self.batch_size = 50
        self.pending_transactions = []

    def _initialize_web3(self) -> Web3:
        """Inizializza Web3 con fallback automatico"""
        web3 = Web3(Web3.HTTPProvider(self.rpc_endpoints[self.current_rpc_index]))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        return web3

    @retry_with_fallback
    def _initialize_contract(self):
        """Inizializza il contratto con gestione errori"""
        try:
            with open('blockchain/contracts/GoldSystem.json') as f:
                contract_json = json.load(f)

            contract = self.web3.eth.contract(
                address=self.web3.to_checksum_address('0x742d35Cc6634C0532925a3b844Bc454e4438f44e'),
                abi=contract_json['abi']
            )
            return contract
        except Exception as e:
            logger.error(f"Contract initialization failed: {str(e)}")
            raise

    async def process_batch_transformation(self, transformations: List[GoldTransformation]):
        """Processa un batch di trasformazioni oro"""
        if not transformations:
            return

        try:
            addresses = []
            amounts = []
            timestamps = []

            for t in transformations:
                addresses.append(self.web3.to_checksum_address(t.user_address))
                amounts.append(self.web3.to_wei(t.gold_grams, 'ether'))
                timestamps.append(int(t.created_at.timestamp()))

            gas_price = await self._get_optimal_gas_price()

            nonce = self.web3.eth.get_transaction_count(
                self.web3.to_checksum_address('0x742d35Cc6634C0532925a3b844Bc454e4438f44e')
            )

            batch_tx = self.contract.functions.batchTransform(
                addresses,
                amounts,
                timestamps
            ).build_transaction({
                'from': self.web3.to_checksum_address('0x742d35Cc6634C0532925a3b844Bc454e4438f44e'),
                'gas': 2000000,
                'gasPrice': gas_price,
                'nonce': nonce,
            })

            private_key = os.environ.get('PRIVATE_KEY')
            if not private_key:
                raise ValueError("Private key not configured")
            signed_tx = self.web3.eth.account.sign_transaction(
                batch_tx,
                private_key=private_key
            )

            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)

            if receipt.status == 1:
                logger.info(f"Batch processed successfully: {tx_hash.hex()}")
                return receipt
            else:
                raise Exception("Batch transaction failed")

        except Exception as e:
            logger.error(f"Batch processing failed: {str(e)}")
            await self._handle_batch_failure(transformations, str(e))
            raise

    async def _get_optimal_gas_price(self) -> int:
        try:
            base_fee = self.web3.eth.get_block('latest').baseFeePerGas
            max_priority_fee = self.web3.eth.max_priority_fee
            gas_price = base_fee + max_priority_fee + self.web3.to_wei(0.1, 'gwei')
            return min(gas_price, self.web3.to_wei(30, 'gwei'))
        except Exception as e:
            logger.warning(f"Error getting optimal gas price: {str(e)}")
            return self.web3.to_wei(20, 'gwei')

    async def _switch_rpc_endpoint(self):
        """Cambia endpoint RPC in caso di problemi"""
        self.current_rpc_index = (self.current_rpc_index + 1) % len(self.rpc_endpoints)
        self.web3 = self._initialize_web3()
        self.contract = self._initialize_contract()
        logger.info(f"Switched to RPC endpoint: {self.rpc_endpoints[self.current_rpc_index]}")

    async def _handle_batch_failure(self, transformations: List[GoldTransformation], error: str):
        """Gestisce il fallimento di un batch"""
        try:
            for t in transformations:
                t.status = 'failed'
                t.error_message = error
            db.session.commit()
            logger.error(f"Batch processing failed: {error}")

            # Ritenta la transazione
            if "nonce too low" in error.lower():
                await self._switch_rpc_endpoint()
                return await self.process_batch_transformation(transformations)

        except Exception as e:
            logger.error(f"Error handling batch failure: {str(e)}")
            db.session.rollback()