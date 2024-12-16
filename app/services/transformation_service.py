from decimal import Decimal
from datetime import datetime
from typing import Dict
from app import db
from app.models.models import User, MoneyAccount, GoldAccount, GoldTransformation
from app.services.blockchain_service import BlockchainService


class TransformationService:
    def __init__(self, blockchain_service=None):
        """Inizializza il servizio con il supporto al mock."""
        self.organization_fee = Decimal('0.05')  # 5% struttura
        self.affiliate_fee = Decimal('0.017')    # 1.7% affiliati
        self.total_fee = self.organization_fee + self.affiliate_fee
        self.blockchain_service = blockchain_service or BlockchainService()

    async def transform_to_gold(self, user_id: int, fixing_price: Decimal) -> Dict:
        """Trasforma il saldo euro dell'utente in oro."""
        try:
            # Debugging
            print(f"Debug: Starting transformation for user {user_id}")

            if fixing_price <= 0:
                return self._error_response('Fixing price non valido')

            # Recupera gli account
            user, money_account, gold_account = self._get_user_and_accounts(user_id)
            if not user or not money_account or not gold_account:
                return self._error_response('Utente o account non trovati')

            if money_account.balance <= 0:
                return self._error_response('Saldo insufficiente')

            # Calcola i grammi di oro da trasformare
            gross_amount = money_account.balance
            net_amount = gross_amount * (1 - self.total_fee)
            gold_grams = net_amount / fixing_price

            # Registra su blockchain
            blockchain_success = await self.blockchain_service.add_to_batch(
                user_address=user.blockchain_address,
                euro_amount=gross_amount,
                gold_grams=gold_grams,
                fixing_price=fixing_price
            )

            if not blockchain_success:
                return self._error_response('Errore nella registrazione blockchain')

            # Registra la trasformazione nel database
            transformation = self._record_transformation(
                user_id, gross_amount, gold_grams, fixing_price
            )
            money_account.balance = Decimal('0')
            gold_account.balance += gold_grams
            gold_account.last_update = datetime.utcnow()

            db.session.commit()

            return self._success_response(transformation, gross_amount, net_amount, gold_grams, fixing_price)
        except Exception as e:
            db.session.rollback()
            return self._error_response(f'Errore nella trasformazione: {str(e)}')

    async def process_weekly_transformations(self, fixing_price: Decimal) -> Dict:
        """Processa tutte le trasformazioni settimanali."""
        try:
            accounts = MoneyAccount.query.filter(MoneyAccount.balance > 0).all()
            results, total_grams, success_count, error_count = [], Decimal('0'), 0, 0

            for account in accounts:
                result = await self.transform_to_gold(account.user_id, fixing_price)
                if result['status'] == 'success':
                    success_count += 1
                    total_grams += Decimal(str(result['transaction']['gold_grams']))
                else:
                    error_count += 1
                results.append(result)

            blockchain_result = await self.blockchain_service.process_batch()

            if blockchain_result['status'] != 'success':
                return self._error_response(blockchain_result['message'])

            return {
                'status': 'success',
                'summary': {
                    'total_processed': len(results),
                    'success_count': success_count,
                    'error_count': error_count,
                    'total_grams': float(total_grams),
                    'blockchain_tx': blockchain_result.get('transaction_hash')
                },
                'transactions': results
            }
        except Exception as e:
            return self._error_response(f'Errore nel processo settimanale: {str(e)}')

    async def get_transformation_history(self, user_id: int) -> Dict:
        """Recupera lo storico delle trasformazioni di un utente."""
        try:
            user = User.query.get(user_id)
            if not user:
                return {
                    'status': 'error',
                    'message': 'Utente non trovato'
                }

            # Recupera trasformazioni dal DB
            transformations = GoldTransformation.query.filter_by(user_id=user_id).all()

            # Recupera storico dalla blockchain
            blockchain_history = await self.blockchain_service.get_user_transactions(user.blockchain_address)

            return {
                'status': 'success',
                'history': [t.to_dict() for t in transformations],
                'blockchain_history': blockchain_history
            }
        except Exception as e:
            return self._error_response(f'Errore nel recupero storico: {str(e)}')

    def _get_user_and_accounts(self, user_id: int):
        """Recupera l'utente e i suoi account."""
        user = db.session.get(User, user_id)
        money_account = MoneyAccount.query.filter_by(user_id=user_id).first()
        gold_account = GoldAccount.query.filter_by(user_id=user_id).first()
        return user, money_account, gold_account

    def _record_transformation(self, user_id: int, euro_amount: Decimal, gold_grams: Decimal, fixing_price: Decimal):
        """Crea un record di trasformazione."""
        transformation = GoldTransformation(
            user_id=user_id,
            euro_amount=euro_amount,
            gold_grams=gold_grams,
            fixing_price=fixing_price
        )
        db.session.add(transformation)
        return transformation

    def _error_response(self, message: str) -> Dict:
        """Genera una risposta di errore."""
        return {'status': 'error', 'message': message}

    def _success_response(self, transformation, gross_amount, net_amount, gold_grams, fixing_price):
        """Genera una risposta di successo."""
        return {
            'status': 'success',
            'transaction': {
                'id': transformation.id,
                'original_amount': float(gross_amount),
                'net_amount': float(net_amount),
                'gold_grams': float(gold_grams),
                'fixing_price': float(fixing_price)
            }
        }