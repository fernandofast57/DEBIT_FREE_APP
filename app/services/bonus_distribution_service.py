from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional
from app import db
from app.models.models import User, MoneyAccount
from app.models.noble_system import NobleRank, NobleRelation, BonusTransaction

class BonusDistributionService:
    def __init__(self):
        self.bonus_rates = {
            1: Decimal('0.007'),  # Nobile - 0.7%
            2: Decimal('0.005'),  # Visconte - 0.5%
            3: Decimal('0.005')   # Conte - 0.5%
        }

    def distribute_transaction_bonus(self, user_id: int, transaction_amount: Decimal) -> Dict:
        """Distribuisce i bonus per una transazione"""
        try:
            upline = self._get_upline(user_id)
            if not upline:
                return {
                    'status': 'success',
                    'message': 'Nessun upline trovato',
                    'distributions': []
                }

            distributions = []
            total_distributed = Decimal('0')

            for level, (upline_user_id, rank_id) in enumerate(upline, 1):
                if level > 3:  # Solo primi 3 livelli
                    break

                bonus_rate = self.bonus_rates.get(level)
                if not bonus_rate:
                    continue

                bonus_amount = transaction_amount * bonus_rate

                # Registra la transazione bonus
                bonus_tx = BonusTransaction(
                    user_id=upline_user_id,
                    transaction_amount=transaction_amount,
                    bonus_amount=bonus_amount,
                    rank_id=rank_id
                )
                db.session.add(bonus_tx)

                # Aggiorna il saldo dell'account
                money_account = MoneyAccount.query.filter_by(user_id=upline_user_id).first()
                if money_account:
                    money_account.balance += bonus_amount
                    total_distributed += bonus_amount

                distributions.append({
                    'user_id': upline_user_id,
                    'rank_id': rank_id,
                    'bonus_rate': float(bonus_rate),
                    'bonus_amount': float(bonus_amount)
                })

            db.session.commit()

            return {
                'status': 'success',
                'total_distributed': float(total_distributed),
                'distributions': distributions
            }

        except Exception as e:
            db.session.rollback()
            return {
                'status': 'error',
                'message': f'Errore nella distribuzione bonus: {str(e)}'
            }

    def _get_upline(self, user_id: int) -> Optional[List[tuple]]:
        """Recupera l'upline dell'utente con i relativi ranghi"""
        try:
            upline = []
            current_id = user_id

            for level in range(1, 4):  # Max 3 livelli
                relation = NobleRelation.query.filter_by(
                    referred_id=current_id
                ).first()

                if not relation:
                    break

                upline.append((relation.referrer_id, relation.rank_id))
                current_id = relation.referrer_id

            return upline

        except Exception:
            return None

    def get_user_bonus_history(self, user_id: int) -> Dict:
        """Recupera lo storico bonus di un utente"""
        try:
            bonus_transactions = BonusTransaction.query.filter_by(user_id=user_id).all()

            return {
                'status': 'success',
                'history': [{
                    'id': tx.id,
                    'transaction_amount': float(tx.transaction_amount),
                    'bonus_amount': float(tx.bonus_amount),
                    'rank_id': tx.rank_id,
                    'date': tx.created_at.isoformat()
                } for tx in bonus_transactions]
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Errore nel recupero storico: {str(e)}'
            }