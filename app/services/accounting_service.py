from decimal import Decimal
from datetime import datetime
from app.models.accounting import GoldInventory, AccountingEntry
from app import db
from app.services.blockchain_service import BlockchainService

class AccountingService:
    def record_gold_purchase(self, grams: Decimal, price_per_gram: Decimal) -> GoldInventory:
        inventory = GoldInventory(
            grams=grams,
            purchase_price=price_per_gram
        )
        entry = AccountingEntry(
            entry_type='purchase',
            amount_eur=grams * price_per_gram,
            amount_gold=grams,
            gold_price=price_per_gram
        )
        try:
            db.session.add_all([inventory, entry])
            db.session.commit()
            return inventory
        except Exception as e:
            db.session.rollback()
            raise  # Re-raise the exception after rollback

    def record_gold_distribution(self, grams: Decimal, user_id: int) -> None:
        inventory = GoldInventory.query.filter_by(
            status='available'
        ).order_by(GoldInventory.purchase_date.asc()).first()
        
        if inventory.grams < grams:
            raise ValueError("Insufficient gold in inventory")
        
        try:
            inventory.grams -= grams
            if inventory.grams == 0:
                inventory.status = 'distributed'
            
            entry = AccountingEntry(
                entry_type='distribution',
                amount_gold=grams,
                reference_id=f'USER-{user_id}'
            )
            db.session.add(entry)

            # Integrating Blockchain Service to log transaction
            tx = BlockchainService()  # Initialize your blockchain service here
            tx_hash = tx.send_transaction(data={ 
                'user_id': user_id,
                'grams': grams,
                'transaction_type': 'distribution'
            })
            # Optionally, store tx_hash with your AccountingEntry if needed

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise

    def get_inventory_summary(self) -> dict:
        total_gold = db.session.query(
            db.func.sum(GoldInventory.grams)
        ).filter_by(status='available').scalar() or Decimal('0')
        
        return {
            'total_gold_grams': float(total_gold),
            'last_update': datetime.utcnow().isoformat()
        }