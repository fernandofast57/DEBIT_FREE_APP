
import pytest
from app.services.blockchain_service import BlockchainService
from decimal import Decimal
import os

@pytest.fixture
async def blockchain_service():
    service = BlockchainService()
    if not service.is_connected():
        pytest.skip("Blockchain connection not available")
    return service

@pytest.mark.asyncio
async def test_gold_transformation(blockchain_service):
    try:
        result = await blockchain_service.record_gold_transaction(
            "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            Decimal("100.0"),
            Decimal("1.5")
        )
        assert result['status'] == 'verified', f"Transaction failed: {result.get('message', 'Unknown error')}"
    except Exception as e:
        pytest.fail(f"Test failed: {str(e)}")

@pytest.mark.asyncio
async def test_bonus_distribution(blockchain_service):
    try:
        result = await blockchain_service.process_batch_transformation([{
            "user_id": 1,
            "amount": Decimal("100.0"),
            "timestamp": 1645564800
        }])
        assert result.status == 1, f"Batch processing failed: {result}"
    except Exception as e:
        pytest.fail(f"Test failed: {str(e)}")
