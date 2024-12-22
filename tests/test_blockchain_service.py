
import pytest
from web3 import Web3, EthereumTesterProvider
from decimal import Decimal
from app.services.blockchain_service import BlockchainService

@pytest.fixture
def blockchain_service():
    w3 = Web3(EthereumTesterProvider())
    service = BlockchainService()
    service.w3 = w3
    service.account = w3.eth.accounts[0]
    return service

@pytest.mark.asyncio
async def test_batch_transform(blockchain_service):
    """Test batch transformation with multiple transactions"""
    users = [blockchain_service.w3.eth.accounts[1]]
    euro_amounts = [Decimal('1000')]
    gold_amounts = [Decimal('0.5')]
    fixing_price = Decimal('1800')
    
    result = await blockchain_service.process_batch_transformation(
        users, euro_amounts, gold_amounts, fixing_price
    )
    assert result is not None
    assert result.status == 1

@pytest.mark.asyncio
async def test_noble_rank_update(blockchain_service):
    """Test noble rank update on blockchain"""
    address = blockchain_service.w3.eth.accounts[1]
    new_rank = 2
    
    receipt = await blockchain_service.update_noble_rank(address, new_rank)
    assert receipt is not None
    assert receipt.status == 1

@pytest.mark.asyncio
async def test_gas_optimization(blockchain_service):
    """Test gas price optimization"""
    gas_price = await blockchain_service._get_optimal_gas_price()
    assert gas_price > 0
    assert gas_price <= Web3.to_wei(30, 'gwei')
