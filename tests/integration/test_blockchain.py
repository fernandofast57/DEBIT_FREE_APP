
import pytest
from unittest.mock import Mock, patch
from app.services.blockchain_service import BlockchainService
import os
from decimal import Decimal

@pytest.fixture
async def blockchain_service():
    service = BlockchainService()
    # Simuliamo una connessione sempre attiva
    service.w3 = Mock()
    service.w3.is_connected.return_value = True
    service.contract = Mock()
    service.account = Mock(address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e')
    return service

@pytest.mark.asyncio
async def test_batch_transformation_process(blockchain_service):
    """Test batch transformation process"""
    batch_data = [
        {"user_id": 1, "amount": 100.0, "timestamp": 1645564800},
        {"user_id": 2, "amount": 200.0, "timestamp": 1645564800}
    ]
    
    blockchain_service.w3.eth.wait_for_transaction_receipt.return_value = Mock(status=1)
    result = await blockchain_service.process_batch_transformation(batch_data)
    assert result is not None
    assert hasattr(result, 'status')
    assert result.status == 1

@pytest.mark.asyncio
async def test_noble_rank_update(blockchain_service):
    """Test noble rank update"""
    blockchain_service.w3.eth.wait_for_transaction_receipt.return_value = Mock(
        status=1,
        transactionHash=b'123456',
        blockNumber=1234
    )
    
    result = await blockchain_service.update_noble_rank(
        "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        1
    )
    assert result['status'] == 'verified'

@pytest.mark.asyncio
async def test_blockchain_stats(blockchain_service):
    """Test blockchain statistics retrieval"""
    blockchain_service.w3.eth.gas_price = 20000000000
    blockchain_service.w3.eth.block_number = 1234567
    blockchain_service.w3.eth.chain_id = 80001
    blockchain_service.w3.eth.syncing = False
    blockchain_service.w3.net.peer_count = 10
    
    stats = await blockchain_service.get_transaction_stats()
    assert stats['status'] == 'verified'
    assert 'gas_price' in stats['stats']
