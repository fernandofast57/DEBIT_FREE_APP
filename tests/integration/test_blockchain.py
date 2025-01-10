import pytest
from unittest.mock import Mock, patch
from app.services.blockchain_service import BlockchainService
from decimal import Decimal

@pytest.fixture
async def blockchain_service():
    service = BlockchainService()
    service.w3 = Mock()
    service.w3.is_connected.return_value = True
    service.contract = Mock()
    return service

@pytest.mark.asyncio
async def test_batch_transformation_process(blockchain_service):
    batch_data = [
        {"user_id": 1, "amount": Decimal('100.0'), "timestamp": 1645564800},
        {"user_id": 2, "amount": Decimal('200.0'), "timestamp": 1645564800}
    ]

    blockchain_service.contract.functions.processBatchTransformation.return_value.transact.return_value = '0x123'
    blockchain_service.w3.eth.wait_for_transaction_receipt.return_value = Mock(status=1)

    result = await blockchain_service.process_batch_transformation(batch_data)
    assert result['status'] == 'success'

@pytest.mark.asyncio
async def test_noble_rank_update(blockchain_service):
    blockchain_service.contract.functions.updateNobleRank.return_value.transact.return_value = '0x123'
    blockchain_service.w3.eth.wait_for_transaction_receipt.return_value = Mock(status=1)

    result = await blockchain_service.update_noble_rank('0x742d35Cc6634C0532925a3b844Bc454e4438f44e', 1)
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