
import pytest
from app.services.blockchain_service import BlockchainService
import os

@pytest.fixture
def blockchain_service():
    """Fixture to provide a blockchain service instance"""
    if not os.getenv('RPC_ENDPOINTS'):
        pytest.skip("RPC_ENDPOINTS not configured")
    return BlockchainService()

def test_blockchain_connection(blockchain_service):
    """Test blockchain service connection"""
    assert blockchain_service.is_connected(), "Blockchain connection failed"

@pytest.mark.asyncio
async def test_noble_rank_update(blockchain_service):
    """Test noble rank update on blockchain"""
    if not blockchain_service.is_connected():
        pytest.skip("Blockchain not connected")
        
    result = await blockchain_service.update_noble_rank(
        address="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        rank=1
    )
    assert result['status'] in ['verified', 'rejected']
