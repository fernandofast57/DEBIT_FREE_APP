
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any
from app import db
from app.models.models import User, MoneyAccount, GoldAccount, Transaction, GoldTransformation
from app.services.blockchain_service import BlockchainService
from app.services.validators.transaction_validator import TransactionValidator

class TransformationService:
    def __init__(self):
        self.validator = TransactionValidator()
        self.blockchain_service = BlockchainService()
        self.structure_fee = Decimal('0.05')

    async def transform_to_gold(self, user_id: int, fixing_price: Decimal) -> Dict[str, Any]:
        async with db.session.begin_nested():
            try:
                user = await User.query.get(user_id)
                if not user:
                    return {'status': 'error', 'message': 'User not found'}
                    
                money_account = await MoneyAccount.query.filter_by(user_id=user_id).first()
                if not money_account:
                    return {'status': 'error', 'message': 'Money account not found'}
                
                if not money_account.balance > 0:
                    return {'status': 'error', 'message': 'Insufficient balance'}

                # Constants from glossary
                # Constants defined in glossary
                USER_SHARE = 0.933  # 93.3% for client
                PLATFORM_FEE = 0.067  # 6.7% platform fee
                
                # Calculate amounts based on glossary definitions
                euro_amount = money_account.balance
                net_amount = euro_amount * CLIENT_SHARE
                gold_grams = net_amount / fixing_price
                
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
                
                return {
                    'status': 'success',
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

    async def validate_transformation(self, euro_amount: Decimal, fixing_price: Decimal) -> bool:
        if euro_amount <= 0:
            return False
        if fixing_price <= 0:
            return False
        return True
