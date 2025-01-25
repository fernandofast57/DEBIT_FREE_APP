from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Any
from app.models import db
from app.models.models import User, MoneyAccount, Transaction
from app.services.blockchain_service import BlockchainService
from app.services.validators.blockchain_validator import BlockchainValidator
import os
import logging

logger = logging.getLogger(__name__)

class BatchCollectionService:
    """Service for managing batch collection operations according to glossary"""
    VALID_TRANSACTION_TYPES = ['gold_transfer', 'noble_verification', 'gold_transformation']
    def __init__(self):
        self.blockchain_service = BlockchainService()
        self.validator = BlockchainValidator(os.getenv('RPC_ENDPOINTS').split(',')[0])
        self.batch_size = 100  # Increased for better throughput
        self.max_retries = 3
        self.concurrent_batches = 5
        self.pending_transfers = []
        self.max_batch_size = 1000 #Added max batch size
        self.daily_batch_limit = 100000 #Added daily limit
        self.MAX_BATCH_AMOUNT = 100000 # Added MAX_BATCH_AMOUNT


    async def validate_batch(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validazione approfondita del batch"""
        try:
            total_amount = Decimal('0')
            errors = []

            for transaction in transactions:
                if not isinstance(transaction.get('amount'), (int, float, Decimal)):
                    errors.append(f"Importo non valido per transazione {transaction.get('id')}")
                    continue

                amount = Decimal(str(transaction['amount']))
                if amount <= 0:
                    errors.append(f"Importo deve essere positivo: {transaction.get('id')}")
                    continue

                total_amount += amount

            if total_amount > self.MAX_BATCH_AMOUNT:
                errors.append(f"Importo totale batch ({total_amount}) supera il limite")

            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'total_amount': total_amount
            }

        except Exception as e:
            logger.error(f"Errore validazione batch: {str(e)}")
            return {'valid': False, 'errors': [str(e)], 'total_amount': Decimal('0')}


    async def execute_batch_transfers(self, batch_transfers: List[Dict]) -> Dict:
        """Processa un batch di bonifici"""
        try:
            transactions = []
            async with self.session_lock:
                for transfer in batch_transfers:
                    transaction = Transaction(
                    user_id=transfer['user_id'],
                    amount=Decimal(str(transfer['amount'])),
                    type='bank_transfer',
                    status='pending',
                    reference=transfer.get('reference', '')
                )
                transactions.append(transaction)

            # Process transactions in optimized batches
            batch_size = 50 #Added batch size
            for i in range(0, len(transactions), batch_size):
                batch = transactions[i:i + batch_size]
                try:
                    db.session.add_all(batch)
                    db.session.commit()
                except Exception as e:
                    logging.error(f"Batch processing error: {e}")
                    db.session.rollback()
                    continue


            # Prepara dati per blockchain
            blockchain_batch = [{
                'user_id': t.user_id,
                'amount': float(t.amount),
                'timestamp': int(t.created_at.timestamp())
            } for t in transactions]

            validation_result = await self.verify_batch(blockchain_batch)
            if validation_result['status'] != 'completed': #This line needs to be adjusted because the new validate_batch returns a dict with 'valid' key
                db.session.rollback()
                return validation_result

            # Processa su blockchain
            receipt = await self.blockchain_service.process_batch_transformation(blockchain_batch)

            if receipt and receipt.status == 1:
                for t in transactions:
                    t.status = 'completed'
                    t.blockchain_tx = receipt.transactionHash.hex()
                db.session.commit()

                return {
                    'status': 'success',
                    'message': f'Processati {len(transactions)} bonifici',
                    'tx_hash': receipt.transactionHash.hex()
                }

            raise Exception("Blockchain transaction failed")

        except Exception as e:
            db.session.rollback()
            logger.exception(f"Error processing batch transfers: {e}")
            return {'status': 'error', 'message': str(e)}