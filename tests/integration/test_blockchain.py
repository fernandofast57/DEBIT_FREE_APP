
import pytest
from app.services.blockchain_service import BlockchainService
import os
from decimal import Decimal

@pytest.fixture
def blockchain_service():
    if not os.getenv('RPC_ENDPOINTS'):
        pytest.skip("RPC_ENDPOINTS not configured")
    return BlockchainService()

@pytest.mark.asyncio
async def test_batch_transformation_process(blockchain_service):
    """Test batch transformation process"""
    if not blockchain_service.is_connected():
        pytest.skip("Blockchain not connected")
        
    batch_data = [
        {"user_id": 1, "amount": 100.0, "timestamp": 1645564800},
        {"user_id": 2, "amount": 200.0, "timestamp": 1645564800}
    ]
    
    result = await blockchain_service.process_batch_transformation(batch_data)
    assert result is not None
    assert hasattr(result, 'status')
    assert result.status == 1

@pytest.mark.asyncio
async def test_noble_rank_update(blockchain_service):
    """Test noble rank update"""
    if not blockchain_service.is_connected():
        pytest.skip("Blockchain not connected")
        
    result = await blockchain_service.update_noble_rank(
        "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        1
    )
    assert result['status'] == 'verified'

@pytest.mark.asyncio
async def test_blockchain_stats(blockchain_service):
    """Test blockchain statistics retrieval"""
    if not blockchain_service.is_connected():
        pytest.skip("Blockchain not connected")
        
    stats = await blockchain_service.get_transaction_stats()
    assert stats['status'] == 'verified'
    assert 'gas_price' in stats['stats']
