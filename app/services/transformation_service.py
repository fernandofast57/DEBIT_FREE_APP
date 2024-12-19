
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional, Any
from app import db
from app.models.models import User, MoneyAccount, GoldAccount, Transaction, GoldTransformation

class TransformationService:
    def __init__(self):
        self.structure_fee = Decimal('0.05')  # 5% struttura
        self.referral_rates = {
            1: Decimal('0.007'),  # 0.7% primo livello
            2: Decimal('0.005'),  # 0.5% secondo livello
            3: Decimal('0.005')   # 0.5% terzo livello
        }

    def validate_transfer(self, technician_id: int, transaction_id: int) -> Dict[str, Any]:
        """Validazione del bonifico da parte del tecnico"""
        try:
            if not self._is_authorized_technician(technician_id):
                return {'status': 'error', 'message': 'Tecnico non autorizzato'}

            transaction = Transaction.query.get(transaction_id)
            if not transaction or transaction.status != 'pending':
                return {'status': 'error', 'message': 'Transazione non valida'}

            # Aggiorna saldo euro cliente
            money_account = MoneyAccount.query.filter_by(user_id=transaction.user_id).first()
            money_account.balance += transaction.amount
            
            transaction.status = 'validated'
            transaction.validation_date = datetime.utcnow()
            transaction.validated_by = technician_id
            
            db.session.commit()
            return {'status': 'success', 'message': 'Bonifico validato'}

        except Exception as e:
            db.session.rollback()
            return {'status': 'error', 'message': str(e)}

    def execute_tuesday_gold_purchase(self, technician_id: int, fixing_price: Decimal) -> Dict[str, Any]:
        """Esegue l'acquisto dell'oro del martedì e distribuisce ai clienti"""
        try:
            if not self._is_authorized_technician(technician_id):
                return {'status': 'error', 'message': 'Tecnico non autorizzato'}
            
            if datetime.utcnow().weekday() != 1:  # Verifica che sia martedì
                return {'status': 'error', 'message': 'Le trasformazioni sono permesse solo il martedì'}

            # Recupera tutti gli account con saldo positivo
            accounts = MoneyAccount.query.filter(MoneyAccount.balance > 0).all()
            if not accounts:
                return {'status': 'success', 'message': 'Nessun account con saldo da processare'}

            total_euro = sum(account.balance for account in accounts)
            structure_fee_amount = total_euro * self.structure_fee
            net_amount = total_euro - structure_fee_amount

            transformations = []
            for account in accounts:
                # Calcola oro per cliente (al netto della fee struttura)
                client_net_amount = account.balance * (1 - self.structure_fee)
                gold_grams = client_net_amount / fixing_price
                
                transformation = GoldTransformation(
                    user_id=account.user_id,
                    euro_amount=account.balance,
                    gold_grams=gold_grams,
                    fixing_price=fixing_price,
                    status='completed',
                    fee_amount=account.balance * self.structure_fee
                )
                transformations.append(transformation)
                
                # Aggiorna saldi
                gold_account = GoldAccount.query.filter_by(user_id=account.user_id).first()
                gold_account.balance += gold_grams
                account.balance = Decimal('0')
                
                # Distribuisci bonus referral
                self._distribute_referral_bonus(account.user_id, gold_grams)

            db.session.add_all(transformations)
            db.session.commit()
            
            return {
                'status': 'success',
                'summary': {
                    'total_euro': float(total_euro),
                    'structure_fee': float(structure_fee_amount),
                    'net_amount': float(net_amount),
                    'transformations_count': len(transformations)
                }
            }

        except Exception as e:
            db.session.rollback()
            return {'status': 'error', 'message': str(e)}

    def _distribute_referral_bonus(self, user_id: int, gold_amount: Decimal) -> None:
        """Distribuisce i bonus referral"""
        user = User.query.get(user_id)
        if user.referrer_id:
            for level, rate in self.referral_rates.items():
                referrer = self._get_nth_level_referrer(user, level)
                if referrer:
                    bonus_amount = gold_amount * rate
                    referrer_gold_account = GoldAccount.query.filter_by(user_id=referrer.id).first()
                    referrer_gold_account.balance += bonus_amount

    def _get_nth_level_referrer(self, user: User, level: int) -> Optional[User]:
        """Recupera il referrer di n-esimo livello"""
        current_user = user
        for _ in range(level):
            if not current_user.referrer_id:
                return None
            current_user = User.query.get(current_user.referrer_id)
        return current_user

    def _is_authorized_technician(self, technician_id: int) -> bool:
        """Verifica se l'utente è un tecnico autorizzato"""
        user = User.query.get(technician_id)
        return user and user.role == 'technician'
