
from decimal import Decimal
from datetime import datetime
from typing import Dict, List
from app import db
from app.models.models import User, MoneyAccount, Transaction
from app.services.blockchain_service import BlockchainService
from app.services.validators.blockchain_validator import BlockchainValidator
import os

class BatchCollectionService:
    def __init__(self):
        self.blockchain_service = BlockchainService()
        self.validator = BlockchainValidator(os.getenv('RPC_ENDPOINTS').split(',')[0])
        self.batch_size = 100  # Increased for better throughput
        self.max_retries = 3
        self.concurrent_batches = 5
        self.pending_transfers = []

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
            
            db.session.add_all(transactions)
            db.session.commit()

            # Prepara dati per blockchain
            blockchain_batch = [{
                'user_id': t.user_id,
                'amount': float(t.amount),
                'timestamp': int(t.created_at.timestamp())
            } for t in transactions]

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
            return {'status': 'error', 'message': str(e)}
