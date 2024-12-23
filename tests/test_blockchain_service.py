
import pytest
from web3 import Web3
from decimal import Decimal
from app.services.blockchain_service import BlockchainService
from app.config.constants import STATUS_VERIFIED

@pytest.fixture
def blockchain_service():
    service = BlockchainService()
    service.w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
    return service

@pytest.mark.asyncio
async def test_batch_transform(blockchain_service):
    """Test batch transformation according to glossary definition"""
    result = await blockchain_service.process_batch_transformation(
        user_ids=[1],
        euro_amounts=[Decimal('1000')],
        gold_grams=[Decimal('20')],
        fixing_price=Decimal('50.00')
    )
    assert result['status'] == STATUS_VERIFIED

@pytest.mark.asyncio
async def test_noble_rank_update(blockchain_service):
    """Test noble rank update according to glossary levels"""
    result = await blockchain_service.update_noble_rank(
        user_id=1,
        new_rank='bronze'
    )
    assert result['status'] == STATUS_VERIFIED
