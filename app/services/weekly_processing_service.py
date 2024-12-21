
from decimal import Decimal
from datetime import datetime
from app.models.accounting import AccountingEntry
from app.models.models import User, GoldAccount
from app import db

class WeeklyProcessingService:
    STRUCTURE_FEE = Decimal('0.05')  # 5%
    AFFILIATE_BONUS = {
        'level_1': Decimal('0.007'),  # 0.7%
        'level_2': Decimal('0.005'),  # 0.5%
        'level_3': Decimal('0.005')   # 0.5%
    }
    
    def process_weekly_transactions(self, fixing_price: Decimal):
        # Raccoglie tutte le transazioni della settimana
        weekly_deposits = AccountingEntry.query.filter_by(
            entry_type='deposit',
            processed=False
        ).all()
        
        total_amount = sum(d.amount_eur for d in weekly_deposits)
        
        # Calcola importi
        structure_amount = total_amount * self.STRUCTURE_FEE
        gold_amount = total_amount - structure_amount
        
        # Registra fee struttura
        self._record_structure_fee(structure_amount)
        
        # Calcola e distribuisci oro
        total_gold_grams = gold_amount / fixing_price
        self._distribute_gold(weekly_deposits, total_gold_grams, fixing_price)
        
        # Marca transazioni come processate
        for deposit in weekly_deposits:
            deposit.processed = True
        
        db.session.commit()
    
    def _distribute_gold(self, deposits, total_gold_grams, fixing_price):
        for deposit in deposits:
            # Calcola oro cliente
            client_gold = (deposit.amount_eur * (1 - self.STRUCTURE_FEE)) / fixing_price
            
            # Aggiorna conto oro cliente
            gold_account = GoldAccount.query.filter_by(user_id=deposit.user_id).first()
            gold_account.balance += client_gold
            
            # Distribuisci bonus affiliazione
            self._distribute_affiliate_bonus(deposit.user_id, client_gold)
