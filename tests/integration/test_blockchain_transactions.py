
import pytest
from app.services.blockchain_service import BlockchainService
from decimal import Decimal

@pytest.mark.asyncio
async def test_gold_transformation():
    service = BlockchainService()
    result = await service.record_gold_transaction(
        "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        Decimal("100.0"),
        Decimal("1.5")
    )
    assert result['status'] == 'verified'

@pytest.mark.asyncio
async def test_bonus_distribution():
    service = BlockchainService()
    result = await service.process_batch_transformation([{
        "user_id": 1,
        "amount": Decimal("100.0"),
        "timestamp": 1645564800
    }])
    assert result.status == 1
