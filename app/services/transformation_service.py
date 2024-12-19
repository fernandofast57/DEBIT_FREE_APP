
```python
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional, Any
from app import db
from app.models.models import User, MoneyAccount, GoldAccount, GoldTransformation, Transaction
from app.services.blockchain_service import BlockchainService
from app.utils.logging_config import logger

class TransformationService:
    def __init__(self):
        self.structure_fee = Decimal('0.05')  # 5% struttura
        self.referral_rates = {
            1: Decimal('0.007'),  # 0.7% primo livello
            2: Decimal('0.005'),  # 0.5% secondo livello
            3: Decimal('0.005')   # 0.5% terzo livello
        }

    async def process_fixing_purchase(self, technician_id: int, fixing_price: Decimal) -> Dict[str, Any]:
        """Processa l'acquisto dell'oro al fixing per tutti i clienti con saldo positivo"""
        try:
            if not self._is_authorized_technician(technician_id):
                return {'status': 'error', 'message': 'Tecnico non autorizzato'}

            # Recupera tutti gli account con saldo positivo
            accounts = MoneyAccount.query.filter(MoneyAccount.balance > 0).all()
            total_euro = sum(account.balance for account in accounts)
            
            # Calcola fee struttura
            structure_fee_amount = total_euro * self.structure_fee
            net_amount = total_euro - structure_fee_amount

            results = []
            for account in accounts:
                # Calcola oro per cliente
                client_net_amount = account.balance * (1 - self.structure_fee)
                gold_grams = client_net_amount / fixing_price
                
                # Aggiorna account oro cliente
                gold_account = GoldAccount.query.filter_by(user_id=account.user_id).first()
                gold_account.balance += gold_grams
                
                # Calcola e distribuisci bonus referral
                referral_bonus = self._calculate_referral_bonus(account.user_id, gold_grams)
                
                # Azzera saldo euro
                account.balance = Decimal('0')
                
                results.append({
                    'user_id': account.user_id,
                    'gold_grams': float(gold_grams),
                    'referral_bonus': float(referral_bonus)
                })

            db.session.commit()
            
            return {
                'status': 'success',
                'summary': {
                    'total_euro': float(total_euro),
                    'structure_fee': float(structure_fee_amount),
                    'net_amount': float(net_amount),
                    'transactions': results
                }
            }

        except Exception as e:
            db.session.rollback()
            return {'status': 'error', 'message': str(e)}

    def _calculate_referral_bonus(self, user_id: int, gold_amount: Decimal) -> Decimal:
        """Calcola e distribuisce i bonus referral"""
        user = User.query.get(user_id)
        total_bonus = Decimal('0')
        
        if user.referrer_id:
            for level, rate in self.referral_rates.items():
                referrer = self._get_nth_level_referrer(user, level)
                if referrer:
                    bonus_amount = gold_amount * rate
                    referrer_gold_account = GoldAccount.query.filter_by(user_id=referrer.id).first()
                    referrer_gold_account.balance += bonus_amount
                    total_bonus += bonus_amount
                    
        return total_bonus

    def _get_nth_level_referrer(self, user: User, level: int) -> Optional[User]:
        """Recupera il referrer di n-esimo livello"""
        current_user = user
        for _ in range(level):
            if not current_user.referrer_id:
                return None
            current_user = User.query.get(current_user.referrer_id)
        return current_user
```
