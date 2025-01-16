
from decimal import Decimal
from datetime import datetime
import asyncio
from app.database import db
from app.models.distribution import WeeklyDistributionLog, DistributionSnapshot
from .distribution_backup import DistributionBackup
from .distribution_validator import DistributionValidator

class WeeklyGoldDistribution:
    def __init__(self):
        self.structure_fee = Decimal('0.05')  # 5%
        self.affiliate_fees = {
            1: Decimal('0.007'),  # 0.7%
            2: Decimal('0.005'),  # 0.5%
            3: Decimal('0.005')   # 0.5%
        }
        self.validator = DistributionValidator()
        self.backup = DistributionBackup()

    async def process_distribution(self, fixing_price: Decimal):
        try:
            # Create distribution snapshot
            await self.backup.create_snapshot()
            
            if not await self.validator.validate_fixing_price(fixing_price):
                raise ValueError("Invalid fixing price")

            total_euro = Decimal('0')
            total_gold = Decimal('0')
            processed_users = 0

            async with db.session() as session:
                users = await session.execute(
                    "SELECT id, money_account_balance FROM users WHERE money_account_balance > 0"
                )
                
                for user_id, balance in users:
                    net_amount = balance * (1 - self.structure_fee)
                    gold_amount = net_amount / fixing_price
                    
                    await self.distribute_gold(user_id, gold_amount)
                    await self.distribute_affiliate_bonuses(user_id, gold_amount)
                    
                    total_euro += balance
                    total_gold += gold_amount
                    processed_users += 1

                # Log distribution
                log = WeeklyDistributionLog(
                    processing_date=datetime.utcnow(),
                    fixing_price=fixing_price,
                    total_euro_processed=total_euro,
                    total_gold_distributed=total_gold,
                    users_processed=processed_users,
                    status='completed'
                )
                session.add(log)
                await session.commit()

            return {
                'status': 'success',
                'total_euro': float(total_euro),
                'total_gold': float(total_gold),
                'users_processed': processed_users
            }

        except Exception as e:
            await self.backup.restore_latest_snapshot()
            raise
