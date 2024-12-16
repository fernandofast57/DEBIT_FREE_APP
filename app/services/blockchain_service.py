
from web3 import Web3
from typing import List, Dict
from app.models.models import db, Transaction
from eth_account import Account
import json

class BlockchainService:
    def __init__(self):
        self.w3 = Web3()
        self.contract_address = "0x..."  # Contract address
        
    async def get_user_transactions(self, address: str) -> List[Dict]:
        try:
            transactions = await db.session.execute(
                db.select(Transaction).filter_by(user_address=address)
            )
            return [tx.to_dict() for tx in transactions.scalars()]
        except Exception as e:
            print(f"Error getting transactions: {e}")
            return []
