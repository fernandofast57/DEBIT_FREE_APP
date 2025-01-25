
from datetime import datetime
from decimal import Decimal
import logging
from typing import Dict

class TransformationMonitor:
    def __init__(self):
        self.logger = logging.getLogger('transformation_monitor')
        
    async def log_transformation(self, 
                               user_id: int,
                               euro_amount: Decimal,
                               gold_grams: Decimal,
                               fixing_price: Decimal) -> None:
        """Log dettagliato delle trasformazioni"""
        try:
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': user_id,
                'euro_amount': str(euro_amount),
                'gold_grams': str(gold_grams),
                'fixing_price': str(fixing_price)
            }
            
            self.logger.info(
                f"Transformation executed: {log_data}",
                extra={'transaction_data': log_data}
            )
            
        except Exception as e:
            self.logger.error(f"Error logging transformation: {str(e)}")
            
    async def monitor_performance(self, 
                                start_time: datetime,
                                end_time: datetime) -> Dict:
        """Monitora performance delle trasformazioni"""
        duration = (end_time - start_time).total_seconds()
        return {
            'duration_seconds': duration,
            'timestamp': datetime.utcnow().isoformat()
        }
