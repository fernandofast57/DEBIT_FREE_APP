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

    @performance_monitor.track_time('transformation')
    async def transform_to_gold(self, user_id: int, fixing_price: Decimal) -> Dict[str, Any]:
        from app.services.notification_service import NotificationService
        notification_service = NotificationService()
        async with db.session.begin_nested():
            try:
                user = await User.query.get(user_id)
                if not user:
                    return {'status': 'error', 'message': 'User not found'}
                    
                money_account = await MoneyAccount.query.filter_by(user_id=user_id).first()
                if not money_account or money_account.balance <= 0:
                    return {'status': 'error', 'message': 'Insufficient balance'}
                
                # Calculate amounts
                euro_amount = money_account.balance
                org_fee = euro_amount * Decimal('0.05')  # 5% organizational fee
                net_amount = euro_amount - org_fee
                
                # Convert to gold
                total_gold_grams = net_amount / fixing_price
                customer_gold = total_gold_grams * Decimal('0.983')  # 98.3% to customer
                reward_gold = total_gold_grams * Decimal('0.017')    # 1.7% to rewards

                # Create transformation
                transformation = GoldTransformation(
                    user_id=user_id,
                    euro_amount=euro_amount,
                    gold_grams=customer_gold, #Only customer gold is recorded in transformation
                    fixing_price=fixing_price,
                    fee_amount=org_fee
                )
                
                # Update balances
                money_account.balance = Decimal('0')
                gold_account = await GoldAccount.query.filter_by(user_id=user_id).first()
                if gold_account:
                    gold_account.balance += customer_gold
                else:
                    return {'status': 'error', 'message': 'Gold account not found'} #Handle missing gold account
                
                # Record on blockchain -  Consider updating to reflect reward distribution if needed.
                await self.blockchain_service.record_transformation(
                    user.blockchain_address,
                    float(customer_gold),
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
                        'gold_grams': float(customer_gold),
                        'fixing_price': float(fixing_price),
                        'fee': float(org_fee)
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