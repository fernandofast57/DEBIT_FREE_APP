
from decimal import Decimal
import asyncio
from datetime import datetime
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import db
from app.models.models import User, MoneyAccount, GoldAccount, Transaction
from app.utils.monitoring.performance_monitor import performance_monitor

class WeeklyGoldDistribution:
    def __init__(self):
        self.structure_fee = Decimal('0.05')  # 5%
        self.affiliate_fee = Decimal('0.017')  # 1.7%
        self.total_fee = self.structure_fee + self.affiliate_fee
        self._processing_lock = asyncio.Lock()
        self._backup_state = {}

    async def create_backup(self, session: AsyncSession) -> str:
        backup_id = datetime.utcnow().isoformat()
        users = await session.execute(
            "SELECT id, money_account_balance, gold_account_balance FROM users")
        self._backup_state[backup_id] = {
            user.id: {
                'money_balance': user.money_account_balance,
                'gold_balance': user.gold_account_balance
            }
            for user in users
        }
        return backup_id

    @performance_monitor.track_time("distribution")
    async def process_distribution(self, fixing_price: Decimal) -> Dict:
        if fixing_price <= Decimal('0'):
            raise ValueError("Invalid fixing price")

        async with self._processing_lock:
            try:
                async with db.get_async_session() as session:
                    backup_id = await self.create_backup(session)
                    total_euro = Decimal('0')
                    total_gold = Decimal('0')
                    processed_users = 0

                    users = await session.execute(
                        "SELECT * FROM users WHERE money_account_balance > 0")

                    for user in users:
                        if user.money_account_balance < 0:
                            raise ValueError("Invalid balance")
                            
                        net_amount = user.money_account_balance * (1 - self.total_fee)
                        gold_amount = net_amount / fixing_price

                        await session.execute(
                            """UPDATE gold_accounts 
                               SET balance = balance + :gold
                               WHERE user_id = :user_id""",
                            {'gold': gold_amount, 'user_id': user.id})

                        await session.execute(
                            """UPDATE money_accounts 
                               SET balance = 0 
                               WHERE user_id = :user_id""",
                            {'user_id': user.id})

                        transaction = Transaction(
                            user_id=user.id,
                            euro_amount=user.money_account_balance,
                            gold_amount=gold_amount,
                            fee_amount=user.money_account_balance * self.total_fee,
                            transaction_type='weekly_distribution',
                            status='completed'
                        )
                        session.add(transaction)

                        total_euro += user.money_account_balance
                        total_gold += gold_amount
                        processed_users += 1

                    await session.commit()

                    return {
                        'status': 'success',
                        'total_euro': float(total_euro),
                        'total_gold': float(total_gold),
                        'users_processed': processed_users
                    }

            except Exception as e:
                if backup_id:
                    await self.restore_backup(session, backup_id)
                raise

    async def restore_backup(self, session: AsyncSession, backup_id: str):
        if backup_id in self._backup_state:
            for user_id, balances in self._backup_state[backup_id].items():
                await session.execute(
                    """UPDATE money_accounts 
                       SET balance = :money_balance 
                       WHERE user_id = :user_id""",
                    {'money_balance': balances['money_balance'], 'user_id': user_id})
                await session.execute(
                    """UPDATE gold_accounts 
                       SET balance = :gold_balance 
                       WHERE user_id = :user_id""",
                    {'gold_balance': balances['gold_balance'], 'user_id': user_id})
            await session.commit()
