
from decimal import Decimal
from typing import Dict
import logging

class TransactionValidator:
    def __init__(self):
        self.logger = logging.getLogger('transaction_validator')
        
    def validate_transaction(self, transaction: Dict) -> bool:
        """Validate transaction structure and amounts with strict checks"""
        try:
            required_fields = ['amount', 'sender_id', 'receiver_id', 'transaction_type']
            
            if not all(field in transaction for field in required_fields):
                self.logger.error(f"Missing required fields in transaction: {transaction}")
                return False
                
            # Validate amount precision and range
            amount = Decimal(str(transaction['amount'])).quantize(Decimal('0.0001'))
            if amount <= Decimal('0') or amount > Decimal('1000000'):
                self.logger.error(f"Amount out of valid range: {amount}")
                return False
                
            # Prevent duplicate transactions
            transaction_hash = f"{transaction['sender_id']}_{transaction['receiver_id']}_{amount}_{transaction['transaction_type']}"
            if self._is_duplicate_transaction(transaction_hash):
                self.logger.error(f"Duplicate transaction detected: {transaction_hash}")
                return False
                
            # Verify sufficient balance
            if not self._verify_sufficient_balance(transaction['sender_id'], amount):
                self.logger.error(f"Insufficient balance for transaction")
                return False
                
            return True
            
        except (ValueError, TypeError, decimal.InvalidOperation) as e:
            self.logger.error(f"Transaction validation error: {str(e)}")
            return False
            
    def _is_duplicate_transaction(self, transaction_hash: str) -> bool:
        """Check for duplicate transactions within time window"""
        # Implement duplicate check logic here
        return False
        
    def _verify_sufficient_balance(self, sender_id: int, amount: Decimal) -> bool:
        """Verify sender has sufficient balance"""
        try:
            with db.session() as session:
                balance = session.query(Account.balance).filter_by(user_id=sender_id).scalar()
                return balance >= amount
        except Exception as e:
            self.logger.error(f"Balance verification error: {str(e)}")
            return False
