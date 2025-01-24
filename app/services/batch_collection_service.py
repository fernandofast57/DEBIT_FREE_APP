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
    """Service for processing batch operations as defined in glossary"""
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


    async def validate_batch(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate batch according to glossary definitions"""
        try:
            if len(transactions) > self.max_batch_size:
                return {
                    'status': 'rejected',
                    'message': f'Batch size exceeds maximum of {self.max_batch_size}'
                }

            total_amount = sum(Decimal(str(t.get('amount', 0))) for t in transactions) #using amount instead of euro_amount
            if total_amount > self.daily_batch_limit:
                return {
                    'status': 'rejected',
                    'message': f'Batch total exceeds daily limit of {self.daily_batch_limit} EUR'
                }

            current_hour = datetime.now().hour
            if not (9 <= current_hour <= 17):
                return {
                    'status': 'rejected',
                    'message': 'Batch processing only allowed during market hours (9:00-17:00)'
                }

            return {'status': 'verified', 'message': 'Batch validation successful'}

        except Exception as e:
            logger.error(f"Batch validation error: {str(e)}")
            return {'status': 'rejected', 'message': str(e)}


    async def process_batch_transfers(self, batch_transfers: List[Dict]) -> Dict:
        """Processa un batch di bonifici"""
        try:
            transactions = []
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

            validation_result = await self.validate_batch(blockchain_batch)
            if validation_result['status'] != 'verified':
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