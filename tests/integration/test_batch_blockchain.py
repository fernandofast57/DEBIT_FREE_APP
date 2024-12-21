
import pytest
from app.services.batch_collection_service import BatchCollectionService
from app.services.blockchain_service import BlockchainService
from app.models.models import Transaction
from decimal import Decimal

@pytest.mark.asyncio
async def test_batch_blockchain_integration(app):
    async with app.app_context():
        batch_service = BatchCollectionService()
        
        # Prepara batch di test
        test_batch = [
            {'user_id': 1, 'amount': '100.00', 'reference': 'TEST-BATCH-1'},
            {'user_id': 2, 'amount': '200.00', 'reference': 'TEST-BATCH-2'}
        ]
        
        # Processa batch
        result = await batch_service.process_batch_transfers(test_batch)
        assert result['status'] == 'success'
        assert 'tx_hash' in result
        
        # Verifica transazioni
        transactions = Transaction.query.filter(
            Transaction.reference.in_(['TEST-BATCH-1', 'TEST-BATCH-2'])
        ).all()
        
        assert len(transactions) == 2
        for tx in transactions:
            assert tx.status == 'completed'
            assert tx.blockchain_tx == result['tx_hash']

@pytest.mark.asyncio
async def test_batch_validation(app):
    async with app.app_context():
        batch_service = BatchCollectionService()
        blockchain_service = BlockchainService()
        
        # Test validazione transazione
        tx_hash = '0x123abc'  # Mock transaction hash
        validation = batch_service.validator.validate_transaction(tx_hash)
        assert 'valid' in validation
        assert 'status' in validation
