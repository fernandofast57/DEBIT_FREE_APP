
from web3 import Web3
from typing import List, Dict
from app.models.models import db, Transaction
from eth_account import Account
import json

class BlockchainService:
    def __init__(self, web3_provider: str = "http://0.0.0.0:8545"):
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        
    async def add_to_batch(self, user_address: str, euro_amount: float, 
                          gold_grams: float, fixing_price: float) -> bool:
        try:
            transaction = Transaction(
                user_address=user_address,
                euro_amount=euro_amount,
                gold_grams=gold_grams,
                fixing_price=fixing_price,
                status='pending'
            )
            db.session.add(transaction)
            await db.session.commit()
            return True
        except Exception as e:
            print(f"Error adding to batch: {e}")
            return False

    async def get_user_transactions(self, address: str) -> List[Dict]:
        try:
            result = await db.session.execute(
                db.select(Transaction).filter_by(user_address=address)
            )
            transactions = result.scalars().all()
            return [self._format_transaction(tx) for tx in transactions]
        except Exception as e:
            print(f"Error getting transactions: {e}")
            return []
            
    def _format_transaction(self, tx: Transaction) -> Dict:
        return {
            'id': tx.id,
            'euro_amount': float(tx.euro_amount),
            'gold_grams': float(tx.gold_grams),
            'fixing_price': float(tx.fixing_price),
            'status': tx.status,
            'created_at': tx.created_at.isoformat()
        }
