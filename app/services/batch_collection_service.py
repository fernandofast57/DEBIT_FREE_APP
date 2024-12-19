
from decimal import Decimal
from datetime import datetime
from typing import Dict, List
from app import db
from app.models.models import User, MoneyAccount, Transaction
from app.services.blockchain_service import BlockchainService

class BatchCollectionService:
    def __init__(self):
        self.blockchain_service = BlockchainService()
        self.batch_size = 50
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

    def validate_transfer(self, transaction_id: int, technician_id: int) -> Dict:
        """Validazione del bonifico da parte del tecnico"""
        try:
            transaction = Transaction.query.get(transaction_id)
            if not transaction or transaction.status != 'pending':
                return {'status': 'error', 'message': 'Transazione non valida'}

            # Verifica autorizzazione tecnico
            if not self._is_authorized_technician(technician_id):
                return {'status': 'error', 'message': 'Tecnico non autorizzato'}

            # Aggiorna saldo utente
            account = MoneyAccount.query.filter_by(user_id=transaction.user_id).first()
            account.balance += transaction.amount
            
            # Aggiorna stato transazione
            transaction.status = 'validated'
            transaction.validation_date = datetime.utcnow()
            transaction.validated_by = technician_id
            
            db.session.commit()
            return {'status': 'success', 'message': 'Bonifico validato e saldo aggiornato'}

        except Exception as e:
            db.session.rollback()
            return {'status': 'error', 'message': str(e)}

    def _is_authorized_technician(self, technician_id: int) -> bool:
        """Verifica se l'utente è un tecnico autorizzato"""
        user = User.query.get(technician_id)
        return user and user.role == 'technician'
