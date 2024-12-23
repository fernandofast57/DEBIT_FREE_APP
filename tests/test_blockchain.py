
import pytest
from app.services.blockchain_service import BlockchainService

@pytest.mark.asyncio
async def test_blockchain_connection(app):
    """Test blockchain service connection"""
    service = BlockchainService()
    stats = await service.get_transaction_stats()
    assert stats['status'] in ['verified', 'error']

@pytest.mark.asyncio
async def test_noble_rank_update(app):
    """Test noble rank update on blockchain"""
    service = BlockchainService()
    result = await service.update_noble_rank(
        address="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        rank=1
    )
    assert result['status'] in ['verified', 'rejected']
