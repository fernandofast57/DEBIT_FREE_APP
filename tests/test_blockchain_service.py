# tests/test_blockchain_service.py

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime
import pytest
from web3 import Web3, EthereumTesterProvider
from app.services.blockchain_service import BlockchainService

@pytest.fixture
def blockchain_service(app):
    w3 = Web3(EthereumTesterProvider())
    test_accounts = w3.eth.accounts
    service = BlockchainService()
    service.w3 = w3
    service.account = test_accounts[0]
    return service

def test_blockchain_connection(blockchain_service):
    assert blockchain_service.w3.is_connected()
    
def test_batch_transform(blockchain_service):
    # Test batch transformation logic
    users = [blockchain_service.w3.eth.accounts[1]]
    euro_amounts = [100]
    gold_amounts = [1]
    fixing_price = 1800
    
    result = blockchain_service.batch_transform(
        users, euro_amounts, gold_amounts, fixing_price
    )
    assert result is not None
from web3 import Web3

class TestBlockchainService:
    @pytest.mark.asyncio
    async def test_initialize_web3(self, blockchain_service):
        """Test Web3 initialization"""
        assert blockchain_service.current_rpc_index == 0
        assert len(blockchain_service.rpc_endpoints) > 1

    @pytest.mark.asyncio
    async def test_rpc_fallback(self, blockchain_service):
        """Test RPC endpoint fallback"""
        original_endpoint = blockchain_service.rpc_endpoints[blockchain_service.current_rpc_index]
        await blockchain_service._switch_rpc_endpoint()
        new_endpoint = blockchain_service.rpc_endpoints[blockchain_service.current_rpc_index]
        assert original_endpoint != new_endpoint

    @pytest.mark.asyncio
    async def test_optimal_gas_price(self, blockchain_service, mock_web3):
        """Test gas price optimization"""
        mock_web3.eth.get_block.return_value.baseFeePerGas = Web3.to_wei(10, 'gwei')
        mock_web3.eth.max_priority_fee = Web3.to_wei(2, 'gwei')

        gas_price = await blockchain_service._get_optimal_gas_price()
        assert gas_price <= Web3.to_wei(30, 'gwei')