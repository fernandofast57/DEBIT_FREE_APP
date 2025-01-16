
from decimal import Decimal
from typing import Dict
import logging

class TransactionValidator:
    def __init__(self):
        self.logger = logging.getLogger('transaction_validator')
        
    def validate_transaction(self, transaction: Dict) -> bool:
        """Validate transaction structure and amounts"""
        required_fields = ['amount', 'sender_id', 'receiver_id', 'transaction_type']
        
        if not all(field in transaction for field in required_fields):
            self.logger.error(f"Missing required fields in transaction: {transaction}")
            return False
            
        if transaction['amount'] <= Decimal('0'):
            self.logger.error(f"Invalid transaction amount: {transaction['amount']}")
            return False
            
        return True
