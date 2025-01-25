from decimal import Decimal
import logging
from datetime import datetime
from typing import Dict
from app.database import db
from app.models.models import User, MoneyAccount, GoldAccount, GoldTransformation
from app.utils.monitoring.performance_monitor import performance_monitor

logger = logging.getLogger(__name__)

class WeeklyProcessingService:
    def __init__(self):
        self.structure_fee = Decimal('0.05')  # 5%

    @performance_monitor.track_time('weekly_processing')
    async def process_weekly_transformations(self, fixing_price: Decimal) -> Dict:
        try:
            processed_count = 0
            total_gold = Decimal('0')

            async with db.session.begin():
                users = await User.query.join(MoneyAccount).filter(
                    MoneyAccount.balance > 0
                ).all()

                for user in users:
                    euro_amount = user.money_account.balance
                    net_amount = euro_amount * (1 - self.structure_fee)
                    gold_grams = net_amount / fixing_price

                    # Create transformation record
                    transformation = GoldTransformation(
                        user_id=user.id,
                        euro_amount=euro_amount,
                        gold_grams=gold_grams,
                        fixing_price=fixing_price,
                        fee_amount=euro_amount * self.structure_fee,
                        status='verified',
                        transaction_type='weekly'
                    )

                    # Update accounts
                    user.money_account.balance = Decimal('0')
                    user.gold_account.balance += gold_grams
                    user.gold_account.last_update = datetime.utcnow()

                    db.session.add(transformation)
                    processed_count += 1
                    total_gold += gold_grams

                await db.session.commit()

            return {
                'status': 'success',
                'processed_users': processed_count,
                'total_gold_grams': float(total_gold),
                'fixing_price': float(fixing_price),
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Weekly transformation processing failed: {str(e)}")
            if 'db.session' in locals():
                await db.session.rollback()
            return {
                'status': 'error',
                'message': str(e),
                'processed_users': 0,
                'total_gold_grams': 0
            }
from decimal import Decimal
import logging
from datetime import datetime
from app.utils.monitoring.transformation_monitor import TransformationMonitor

logger = logging.getLogger(__name__)
monitor = TransformationMonitor()

class WeeklyProcessingService:
    def __init__(self):
        self.monitor = monitor
        
    async def process_weekly_transformations(self) -> dict:
        """Elabora le trasformazioni settimanali con monitoraggio"""
        start_time = datetime.utcnow()
        try:
            result = await self._execute_transformations()
            performance_metrics = await self.monitor.monitor_performance(start_time, datetime.utcnow())
            
            return {
                'status': 'success',
                'transformations_processed': result['count'],
                'total_amount': str(result['total_amount']),
                'performance': performance_metrics
            }
            
        except Exception as e:
            logger.error(f"Errore elaborazione settimanale: {str(e)}")
            return {'status': 'error', 'message': str(e)}
