from decimal import Decimal
from datetime import datetime
from typing import List, Dict
from app import db
from app.models.models import User, MoneyAccount, Transaction

class BatchCollectionService:
    def __init__(self):
        self.pending_transactions = []
        self.min_amount = Decimal('100')  # Importo minimo bonifico

    def validate_bank_transfer(self, transfer_id: str, technician_id: int) -> Dict:
        """Convalida manuale di un bonifico da parte del tecnico"""
        try:
            if not self._is_authorized_technician(technician_id):
                return {
                    'status': 'error',
                    'message': 'Tecnico non autorizzato'
                }

            transfer = Transaction.query.filter_by(id=transfer_id, status='pending').first()
            if not transfer:
                return {
                    'status': 'error',
                    'message': 'Bonifico non trovato'
                }

            # Aggiorna stato bonifico e bilancio cliente
            transfer.status = 'validated'
            transfer.validated_by = technician_id
            transfer.validation_date = datetime.utcnow()

            money_account = MoneyAccount.query.filter_by(user_id=transfer.user_id).first()
            money_account.balance += transfer.amount
            money_account.last_update = datetime.utcnow()

            db.session.commit()
            if not transfer:
                return {
                    'status': 'error',
                    'message': 'Bonifico non trovato o già processato'
                }

            # Aggiorna il saldo dell'account del cliente
            money_account = MoneyAccount.query.filter_by(user_id=transfer.user_id).first()
            money_account.balance += transfer.amount
            money_account.last_update = datetime.utcnow()

            # Aggiorna lo stato della transazione
            transfer.status = 'completed'
            transfer.validated_by = technician_id
            transfer.validation_date = datetime.utcnow()

            db.session.commit()

            return {
                'status': 'success',
                'transaction': {
                    'id': transfer.id,
                    'amount': float(transfer.amount),
                    'new_balance': float(money_account.balance)
                }
            }
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

    def process_tuesday_gold_transformation(self) -> Dict:
        """Processa le trasformazioni in oro ogni martedì al fixing"""
        try:
            # Verifica che sia martedì
            if datetime.now().weekday() != 1:  # 1 = Martedì
                return {
                    'status': 'error',
                    'message': 'Le trasformazioni sono permesse solo il martedì'
                }

            # Recupera tutti gli account con saldo positivo
            accounts = MoneyAccount.query.filter(MoneyAccount.balance > 0).all()
            
            if not accounts:
                return {
                    'status': 'success',
                    'message': 'Nessun account da processare',
                    'transactions': []
                }

            transformation_service = TransformationService()
            results = []

            # Processa ogni account
            for account in accounts:
                result = await transformation_service.transform_to_gold(
                    account.user_id,
                    self._get_current_fixing_price()
                )
                results.append(result)

            return {
                'status': 'success',
                'summary': {
                    'total_processed': len(results),
                    'success_count': sum(1 for r in results if r['status'] == 'success'),
                    'error_count': sum(1 for r in results if r['status'] == 'error')
                },
                'transactions': results
            }
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