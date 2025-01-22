
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.exc import SQLAlchemyError
from app.models.accounting import GoldInventory, AccountingEntry
from app.models.models import Transaction
from app.database import db
from app.services.blockchain_service import BlockchainService
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

class AccountingService:
    def __init__(self, blockchain_service: Optional[BlockchainService] = None):
        self.blockchain_service = None
        self._blockchain_service_param = blockchain_service

    async def initialize(self):
        if self.blockchain_service is None:
            self.blockchain_service = self._blockchain_service_param or await BlockchainService()
        
    async def record_gold_transaction(self, 
                                    user_id: int, 
                                    amount: Decimal, 
                                    transaction_type: str) -> Dict[str, Any]:
        """Record a gold transaction with improved validation and error handling"""
        try:
            if amount <= 0:
                raise ValueError("Transaction amount must be positive")
                
            entry = AccountingEntry(
                user_id=user_id,
                amount=amount,
                transaction_type=transaction_type,
                timestamp=datetime.utcnow()
            )
            
            inventory_update = GoldInventory(
                change_amount=amount,
                transaction_type=transaction_type,
                timestamp=datetime.utcnow()
            )
            
            db.session.add(entry)
            db.session.add(inventory_update)
            await db.session.commit()
            
            return {
                'status': 'success',
                'entry_id': entry.id,
                'amount': float(amount),
                'timestamp': entry.timestamp.isoformat()
            }
            
        except SQLAlchemyError as e:
            await db.session.rollback()
            logger.error(f"Database error in record_gold_transaction: {str(e)}")
            return {'status': 'error', 'message': 'Database error occurred'}
            
        except Exception as e:
            logger.error(f"Error in record_gold_transaction: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    async def get_gold_balance(self) -> Decimal:
        """Get current gold balance with error handling"""
        try:
            result = await GoldInventory.query.with_entities(
                db.func.sum(GoldInventory.change_amount)
            ).scalar()
            return Decimal(result or 0)
        except Exception as e:
            logger.error(f"Error getting gold balance: {str(e)}")
            raise

    async def get_transaction_history(self, 
                                    user_id: Optional[int] = None, 
                                    limit: int = 100) -> List[Dict[str, Any]]:
        """Get transaction history with pagination and filtering"""
        try:
            query = AccountingEntry.query.order_by(AccountingEntry.timestamp.desc())
            
            if user_id is not None:
                query = query.filter_by(user_id=user_id)
            
            entries = await query.limit(limit).all()
            
            return [{
                'id': entry.id,
                'user_id': entry.user_id,
                'amount': float(entry.amount),
                'transaction_type': entry.transaction_type,
                'timestamp': entry.timestamp.isoformat()
            } for entry in entries]
            
        except Exception as e:
            logger.error(f"Error getting transaction history: {str(e)}")
            return []

    async def reconcile_transactions(self) -> Dict[str, Any]:
        """Reconcile accounting entries with blockchain transactions"""
        try:
            local_transactions = await AccountingEntry.query.all()
            blockchain_transactions = await self.blockchain_service.get_transaction_history()
            
            discrepancies = []
            for local_tx in local_transactions:
                if not any(btx['id'] == local_tx.blockchain_tx_id 
                          for btx in blockchain_transactions):
                    discrepancies.append({
                        'id': local_tx.id,
                        'amount': float(local_tx.amount),
                        'type': 'missing_on_blockchain'
                    })
            
            return {
                'status': 'success',
                'total_checked': len(local_transactions),
                'discrepancies': discrepancies
            }
            
        except Exception as e:
            logger.error(f"Error in reconciliation: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
