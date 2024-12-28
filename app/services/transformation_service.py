from decimal import Decimal
from datetime import datetime
from typing import Dict, Any
from app.database import db
from app.models.models import User, MoneyAccount, GoldAccount, Transaction, GoldTransformation
from app.services.blockchain_service import BlockchainService
from app.services.validators.transaction_validator import TransactionValidator
from app.utils.performance_monitor import performance_monitor

class TransformationService:
    def __init__(self):
        self.validator = TransactionValidator()
        self.blockchain_service = BlockchainService()
        self.structure_fee = Decimal('0.05')
        
    async def initialize(self):
        """Async initialization"""
        self.blockchain_service = await self.blockchain_service.initialize()

    @performance_monitor.track_time('transformation') # Assumes performance_monitor object exists.  Add import if needed.
    async def transform_to_gold(self, user_id: int, fixing_price: Decimal, euro_amount: Decimal = None, fee_amount: Decimal = None, gold_grams: Decimal = None) -> Dict[str, Any]:
        from app.services.notification_service import NotificationService
        notification_service = NotificationService()
        async with db.session.begin_nested(): # This already provides transaction management; assumes atomicity
            try:
                user = await User.query.get(user_id)
                if not user:
                    return {'status': 'error', 'message': 'User not found'}
                    
                money_account = await MoneyAccount.query.filter_by(user_id=user_id).first()
                if not money_account:
                    return {'status': 'error', 'message': 'Money account not found'}
                
                if not money_account.balance > 0:
                    return {'status': 'error', 'message': 'Insufficient balance'}

                from app.config.constants import CLIENT_SHARE, NETWORK_SHARE, STRUCTURE_FEE
                
                # Calculate amounts according to glossary
                euro_amount = money_account.balance
                structure_fee = euro_amount * STRUCTURE_FEE
                net_amount = euro_amount - structure_fee
                gold_grams = (net_amount * CLIENT_SHARE) / fixing_price
                network_gold = (net_amount * NETWORK_SHARE) / fixing_price
                
                # Create transformation
                transformation = GoldTransformation(
                    user_id=user_id,
                    euro_amount=euro_amount,
                    gold_grams=gold_grams,
                    fixing_price=fixing_price,
                    fee_amount=euro_amount * self.structure_fee
                )
                
                # Update balances
                money_account.balance = Decimal('0')
                gold_account = await GoldAccount.query.filter_by(user_id=user_id).first()
                gold_account.balance += gold_grams
                
                # Record on blockchain
                await self.blockchain_service.record_transformation(
                    user.blockchain_address,
                    float(gold_grams),
                    float(fixing_price)
                )
                
                db.session.add(transformation)
                await db.session.commit()
                
                # Send notification
                await notification_service.notify_transformation(user, transformation)
                
                return {
                    'status': 'verified',
                    'transaction': {
                        'original_amount': float(euro_amount),
                        'gold_grams': float(gold_grams),
                        'fixing_price': float(fixing_price),
                        'fee': float(euro_amount * self.structure_fee)
                    }
                }
            except Exception as e:
                await db.session.rollback()
                return {'status': 'error', 'message': str(e)}

    async def validate_transformation(self, euro_amount: Decimal, fixing_price: Decimal) -> Dict[str, Any]:
        """Validate transformation according to glossary definitions"""
        try:
            # Validate minimum amount
            min_amount = Decimal('100.00')  # Minimum amount from glossary
            if euro_amount < min_amount:
                return {
                    'status': 'rejected', 
                    'message': f'Amount must be at least {min_amount} EUR'
                }

            # Validate fixing price
            if fixing_price <= 0:
                return {
                    'status': 'rejected',
                    'message': 'Invalid fixing price'
                }
                
            # Validate transformation timing
            current_hour = datetime.now().hour
            if not (9 <= current_hour <= 17):  # Market hours 9:00-17:00
                return {
                    'status': 'rejected',
                    'message': 'Transformations only allowed during market hours (9:00-17:00)'
                }

            return {
                'status': 'verified',
                'message': 'Validation successful',
                'details': {
                    'euro_amount': float(euro_amount),
                    'fixing_price': float(fixing_price),
                    'gold_grams': float(euro_amount / fixing_price)
                }
            }
            
        except Exception as e:
            logger.error(f"Transformation validation error: {str(e)}")
            return {'status': 'rejected', 'message': str(e)}