
from decimal import Decimal
from datetime import datetime
from typing import Dict, List
from app import db
from app.models.models import User, MoneyAccount, Transaction

class BatchCollectionService:
    def process_bank_transfer(self, user_id: int, amount: Decimal, transfer_reference: str) -> Dict:
        """Processo iniziale del bonifico - solo validazione"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'status': 'error', 'message': 'Utente non trovato'}

            # Registra il bonifico in stato pending
            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                type='bank_transfer',
                status='pending',
                reference=transfer_reference
            )
            db.session.add(transaction)
            db.session.commit()

            return {
                'status': 'success',
                'message': 'Bonifico registrato in attesa di validazione',
                'transaction_id': transaction.id
            }

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

            return {
                'status': 'success',
                'message': 'Bonifico validato e saldo aggiornato'
            }

        except Exception as e:
            db.session.rollback()
            return {'status': 'error', 'message': str(e)}

    def _is_authorized_technician(self, technician_id: int) -> bool:
        """Verifica se l'utente è un tecnico autorizzato"""
        user = User.query.get(technician_id)
        return user and user.role == 'technician'
