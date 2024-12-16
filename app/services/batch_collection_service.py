from decimal import Decimal
from datetime import datetime
from typing import List, Dict
from app import db
from app.models.models import User, MoneyAccount, Transaction

class BatchCollectionService:
    def __init__(self):
        self.pending_transactions = []
        self.min_amount = Decimal('100')  # Importo minimo bonifico

    def process_bank_transfer(self, user_id: int, amount: Decimal) -> Dict:
        """Processa un singolo bonifico ricorrente"""
        try:
            # Verifica importo minimo
            if amount < self.min_amount:
                return {
                    'status': 'error',
                    'message': f'Importo minimo richiesto: {self.min_amount}€'
                }

            # Recupera gli account (usando la nuova sintassi)
            user = db.session.get(User, user_id)
            if not user:
                return {
                    'status': 'error',
                    'message': 'Utente non trovato'
                }

            money_account = MoneyAccount.query.filter_by(user_id=user_id).first()
            if not money_account:
                return {
                    'status': 'error',
                    'message': 'Conto non trovato'
                }

            # Crea la transazione
            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                type='deposit',
                status='completed'
            )

            # Aggiorna il saldo
            money_account.balance += amount
            money_account.last_update = datetime.utcnow()

            # Salva le modifiche
            db.session.add(transaction)
            db.session.commit()

            return {
                'status': 'success',
                'transaction': {
                    'id': transaction.id,
                    'amount': float(amount),
                    'new_balance': float(money_account.balance)
                }
            }

        except Exception as e:
            db.session.rollback()
            return {
                'status': 'error',
                'message': f'Errore nel processo bonifico: {str(e)}'
            }

    def process_weekly_batch(self) -> Dict:
        """Processa tutti i bonifici ricorrenti della settimana"""
        try:
            results = []
            success_count = 0
            error_count = 0

            # Qui andrebbe la logica per recuperare i bonifici ricorrenti dal sistema bancario
            # Per ora simuliamo con i pending_transactions
            for transaction in self.pending_transactions:
                result = self.process_bank_transfer(
                    transaction['user_id'],
                    transaction['amount']
                )

                if result['status'] == 'success':
                    success_count += 1
                else:
                    error_count += 1

                results.append(result)

            # Pulisce le transazioni processate
            self.pending_transactions = []

            return {
                'status': 'success',
                'summary': {
                    'total_processed': len(results),
                    'success_count': success_count,
                    'error_count': error_count
                },
                'transactions': results
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Errore nel processo batch: {str(e)}'
            }

    def add_to_batch(self, user_id: int, amount: Decimal) -> bool:
        """Aggiunge un bonifico al prossimo batch"""
        try:
            self.pending_transactions.append({
                'user_id': user_id,
                'amount': amount
            })
            return True
        except:
            return False

    def get_pending_batch(self) -> List:
        """Recupera la lista dei bonifici in attesa di processo"""
        return self.pending_transactions