
from decimal import Decimal
from typing import Dict
from app.database import db
from app.models.distribution import WeeklyDistributionLog

class DistributionValidator:
    async def validate_fixing_price(self, fixing_price: Decimal) -> bool:
        if fixing_price <= 0:
            return False
        return True

    async def validate_distribution(self, distribution_data: Dict) -> bool:
        try:
            total_euro = Decimal(str(distribution_data['total_euro']))
            total_gold = Decimal(str(distribution_data['total_gold']))
            
            if total_euro <= 0 or total_gold <= 0:
                return False
                
            # Verify total amounts match individual transactions
            async with db.session() as session:
                result = await session.execute(
                    """
                    SELECT SUM(euro_amount) as total_euro, 
                           SUM(gold_amount) as total_gold 
                    FROM weekly_distribution_logs 
                    WHERE created_at >= NOW() - INTERVAL '1 week'
                    """
                )
                db_totals = result.first()
                
                if abs(db_totals.total_euro - total_euro) > Decimal('0.01'):
                    return False
                    
                if abs(db_totals.total_gold - total_gold) > Decimal('0.00001'):
                    return False
                    
            return True
            
        except Exception:
            return False
