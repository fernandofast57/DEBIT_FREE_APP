
from decimal import Decimal
import logging
from datetime import datetime
from typing import List
from app.database import db
from app.models.models import User, MoneyAccount, GoldAccount, GoldTransformation
from app.services.transformation_service import TransformationService
from app.utils.performance_monitor import performance_monitor

logger = logging.getLogger(__name__)

class WeeklyProcessingService:
    def __init__(self):
        self.structure_fee = Decimal('0.05')  # 5%
        self.transformation_service = TransformationService()
    
    @performance_monitor.track_time('weekly_processing')
    async def process_weekly_transformations(self, fixing_price: Decimal) -> dict:
        """Process all pending weekly transformations"""
        try:
            async with db.session.begin():
                # Get all users with positive money account balance
                users_to_process = await User.query.join(MoneyAccount).filter(
                    MoneyAccount.balance > 0
                ).all()
                
                processed_count = 0
                total_gold = Decimal('0')
                
                for user in users_to_process:
                    result = await self.transformation_service.transform_to_gold(
                        user.id,
                        fixing_price
                    )
                    
                    if result['status'] == 'verified':
                        processed_count += 1
                        total_gold += Decimal(str(result['transaction']['gold_grams']))
                
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
            await db.session.rollback()
            return {
                'status': 'error',
                'message': str(e)
            }
