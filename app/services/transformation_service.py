from decimal import Decimal
from typing import Dict, Any, List
from datetime import datetime
from app.models.models import User, MoneyAccount, GoldAccount
from app.database import db
import logging

logger = logging.getLogger(__name__)

class TransformationService:
    ORGANIZATION_FEE = Decimal('0.05')  # 5% organization fee
    GOLD_TO_EURO_FEE = Decimal('0.03')  # 3% fee for gold to euro conversion
    AFFILIATE_BONUS = {
        1: Decimal('0.007'),  # 0.7% first level
        2: Decimal('0.005'),  # 0.5% second level
        3: Decimal('0.005')   # 0.5% third level
    }

    @staticmethod
    async def verify_transfer(user_id: int, transfer_amount: Decimal) -> Dict[str, Any]:
        """Verify if transfer is valid for transformation with detailed validation"""
        try:
            user = await User.query.get(user_id)
            if not user:
                return {"valid": False, "reason": "User not found"}
            if not user.money_account:
                return {"valid": False, "reason": "No money account found"}
            if transfer_amount <= 0:
                return {"valid": False, "reason": "Invalid amount"}
            if user.money_account.balance < transfer_amount:
                return {"valid": False, "reason": "Insufficient funds"}
            return {"valid": True, "user": user}
        except Exception as e:
            logger.error(f"Transfer verification error: {str(e)}")
            return False

    @staticmethod
    async def process_organization_fee(amount: Decimal) -> Decimal:
        """Process 5% organization fee and return net amount"""
        fee_amount = amount * TransformationService.ORGANIZATION_FEE
        net_amount = amount - fee_amount
        # Here you would add logic to transfer fee to organization account
        return net_amount

    @staticmethod
    async def transform_gold(self, user_id: int, euro_amount: Decimal, fixing_price: Decimal) -> Dict:
        """Transform euros to gold and record on blockchain"""
        try:
            user = await User.query.get(user_id)
            if not user or not user.money_account:
                raise ValueError("Invalid user or money account")

            gold_amount = await self.calculate_gold_amount(euro_amount, fixing_price)

            # Record on blockchain
            blockchain_service = BlockchainService()
            tx_result = await blockchain_service.record_gold_transaction(
                user.blockchain_address,
                float(euro_amount),
                float(gold_amount)
            )

            if tx_result['status'] != 'verified':
                raise ValueError(f"Blockchain transaction failed: {tx_result.get('message')}")

            # Update database
            user.money_account.balance -= euro_amount
            user.gold_account.balance += gold_amount

            transformation = GoldTransformation(
                user_id=user_id,
                euro_amount=euro_amount,
                gold_grams=gold_amount,
                fixing_price=fixing_price,
                blockchain_tx_hash=tx_result['transaction_hash']
            )

            db.session.add(transformation)
            await db.session.commit()

            return {
                'status': 'success',
                'gold_amount': float(gold_amount),
                'transaction_hash': tx_result['transaction_hash']
            }

        except Exception as e:
            await db.session.rollback()
            logger.error(f"Gold transformation error: {str(e)}")
            raise

    async def calculate_gold_amount(euro_amount: Decimal, fixing_price: Decimal) -> Decimal:
        """Calculate gold amount based on fixing price"""
        if fixing_price <= 0:
            logger.error(f"Invalid fixing price: {fixing_price}")
            raise ValueError("Invalid fixing price")
        if euro_amount <= 0:
            logger.error(f"Invalid euro amount: {euro_amount}")
            raise ValueError("Invalid euro amount")

        logger.info(f"Calculating gold amount - Euro: {euro_amount}€, Fixing price: {fixing_price}")
        return euro_amount / fixing_price

    @staticmethod
    async def distribute_affiliate_bonuses(user: User, gold_amount: Decimal):
        """Distribute affiliate bonuses up to 3 levels"""
        try:
            current_user = user
            for level in range(1, 4):
                if not current_user.referrer_id:
                    break

                referrer = await User.query.get(current_user.referrer_id)
                if not referrer:
                    break

                bonus_percentage = TransformationService.AFFILIATE_BONUS[level]
                bonus_amount = gold_amount * bonus_percentage

                if not referrer.gold_account:
                    continue

                referrer.gold_account.balance += bonus_amount
                current_user = referrer

            await db.session.commit()
        except Exception as e:
            logger.error(f"Bonus distribution error: {str(e)}")
            await db.session.rollback()
            raise

    @staticmethod
    async def process_transformation(user_id: int, euro_amount: Decimal, fixing_price: Decimal) -> Dict[str, Any]:
        """Process complete money to gold transformation"""
        logger.info(f"Inizio trasformazione - Utente: {user_id} - Importo: {euro_amount}€ - Fixing: {fixing_price}", 
                    extra={'audit_type': 'TRANSFORMATION_START',
                           'user_id': user_id,
                           'amount': str(euro_amount),
                           'fixing_price': str(fixing_price),
                           'timestamp': datetime.utcnow().isoformat()})

        try:
            # 1. Verifica del trasferimento
            logger.info(f"Controllo disponibilità fondi per utente {user_id}")
            verification_result = await TransformationService.verify_transfer(user_id, euro_amount)
            if not verification_result["valid"]:
                logger.warning(f"Transfer verification failed for user {user_id} - {verification_result['reason']}")
                return {
                    "status": "error",
                    "message": verification_result["reason"]
                }

            # 2. Process organization fee
            logger.info(f"Calcolo commissioni per importo {euro_amount}€")
            net_amount = await TransformationService.process_organization_fee(euro_amount)
            logger.info(f"Importo netto dopo commissioni: {net_amount}€")

            # 3. Calculate gold amount
            logger.info(f"Calcolo grammi oro con fixing price {fixing_price}")
            gold_amount = await TransformationService.calculate_gold_amount(net_amount, fixing_price)
            logger.info(f"Grammi oro calcolati: {gold_amount}g")

            # 4. Process transformation
            async with db.session() as session:
                async with session.begin():
                    user = await User.query.get(user_id)

                    # Update money and gold accounts
                    user.money_account.balance -= euro_amount
                    user.gold_account.balance += gold_amount
                    user.gold_account.last_update = datetime.utcnow()

                    # Distribute affiliate bonuses
                    await TransformationService.distribute_affiliate_bonuses(user, gold_amount)

                    await db.session.commit()
                user = await User.query.get(user_id)

                # Update money and gold accounts
                user.money_account.balance -= euro_amount
                user.gold_account.balance += gold_amount
                user.gold_account.last_update = datetime.utcnow()

                # Distribute affiliate bonuses
                await TransformationService.distribute_affiliate_bonuses(user, gold_amount)

                await db.session.commit()

            return {
                "status": "success",
                "gold_grams": float(gold_amount),
                "transaction_id": None,
                "fees": {
                    "organization": float(euro_amount * TransformationService.ORGANIZATION_FEE),
                    "affiliate_bonus": float(gold_amount * sum(TransformationService.AFFILIATE_BONUS.values()))
                }
            }

        except Exception as e:
            logger.error(f"Transformation error: {str(e)}")
            await db.session.rollback()
            return {
                "status": "error",
                "message": str(e)
            }

    @staticmethod
    async def transform_to_euro(user_id: int, gold_amount: Decimal, fixing_price: Decimal) -> Dict[str, Any]:
        """Transform gold to euros with 3% conversion fee. No affiliate bonuses in this direction."""
        logger.info(f"Starting gold to euro transformation - User: {user_id} - Gold: {gold_amount}g")

        try:
            async with db.session() as session:
                user = await User.query.get(user_id)
                if not user or not user.gold_account:
                    raise ValueError("Invalid user or gold account")

                if user.gold_account.balance < gold_amount:
                    raise ValueError("Insufficient gold balance")

                # Calculate gross euro amount
                gross_euro_amount = gold_amount * fixing_price

                # Calculate net euro amount by dividing by (1 + fee)
                # This ensures the 3% fee is calculated sul netto da trasferire
                net_euro_amount = gross_euro_amount / (1 + TransformationService.GOLD_TO_EURO_FEE)
                fee_amount = gross_euro_amount - net_euro_amount

                # Update gold account
                user.gold_account.balance -= gold_amount
                
                # Create bank transfer record
                bank_transfer = BankTransfer(
                    user_id=user_id,
                    amount=net_euro_amount,
                    iban=user.bank_account.iban,
                    status='pending',
                    description=f'Gold conversion: {gold_amount}g to EUR'
                )
                
                db.session.add(bank_transfer)
                await session.commit()

                return {
                    "status": "success",
                    "euro_amount": float(net_euro_amount),
                    "fee_amount": float(fee_amount),
                    "conversion_rate": float(fixing_price),
                    "transfer_id": bank_transfer.id,
                    "iban": user.bank_account.iban
                }

        except Exception as e:
            logger.error(f"Gold to euro transformation error: {str(e)}")
            await session.rollback()
            raise
from decimal import Decimal
from datetime import datetime
from app.models.models import MoneyAccount, GoldAccount, Transaction
from app.database import db

class TransformationService:
    STRUCTURE_FEE = Decimal('0.05')  # 5%
    NETWORK_FEE = Decimal('0.017')   # 1.7%
    
    async def execute_weekly_transformation(self, fixing_price: Decimal):
        accounts = await MoneyAccount.query.filter(MoneyAccount.balance > 0).all()
        
        for account in accounts:
            euro_amount = account.balance
            total_fee = euro_amount * (self.STRUCTURE_FEE + self.NETWORK_FEE)
            net_amount = euro_amount - total_fee
            gold_grams = net_amount / fixing_price
            
            # Update accounts
            account.balance = Decimal('0')
            account.user.gold_account.balance += gold_grams
            
            # Record transaction
            transaction = Transaction(
                user_id=account.user_id,
                type='transformation',
                euro_amount=euro_amount,
                gold_amount=gold_grams,
                fee_amount=total_fee,
                fixing_price=fixing_price,
                timestamp=datetime.utcnow()
            )
            
            db.session.add(transaction)
        
        await db.session.commit()
