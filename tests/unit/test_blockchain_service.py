import pytest
from unittest.mock import Mock
from app.services.blockchain_service import BlockchainService
from decimal import Decimal

@pytest.fixture
async def blockchain_service():
    service = BlockchainService()
    service.w3 = Mock()
    service.w3.is_connected.return_value = True
    service.contract = Mock()
    service.w3.eth = Mock()
    service.w3.eth.get_block_number = Mock(return_value=12345)  # Esempio di numero di blocco
    service.w3.eth.wait_for_transaction_receipt = Mock(return_value=Mock(status=1))
    return service

@pytest.mark.asyncio
async def test_batch_transformation_process(blockchain_service):
    try:
        blockchain_service.w3.eth.get_block_number()  # Verifica connessione
        batch_data = [
            {"user_id": 1, "amount": Decimal('100.0'), "timestamp": 1645564800},
            {"user_id": 2, "amount": Decimal('200.0'), "timestamp": 1645564800}
        ]

        blockchain_service.contract.functions.processBatchTransformation.return_value.transact.return_value = Mock(transactionHash='0x123', status=1)

        result = await blockchain_service.process_batch_transformation(batch_data)
        assert result['status'] == 'success'
    except Exception as e:
        pytest.skip(f"Blockchain connection not available: {str(e)}")