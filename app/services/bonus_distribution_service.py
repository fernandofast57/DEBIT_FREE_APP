
from decimal import Decimal
from typing import List, Dict
from datetime import datetime
from app import db
from app.models.models import User, GoldAccount, NobleRank
from app.utils.logging_config import logger

class BonusDistributionService:
    def __init__(self):
        self.bonus_rates = {
            'Knight': Decimal('0.01'),  # 1%
            'Baron': Decimal('0.02'),   # 2%
            'Count': Decimal('0.03'),   # 3%
            'Duke': Decimal('0.05')     # 5%
        }
    
    def calculate_user_bonus(self, user: User) -> Decimal:
        if not user.noble_rank:
            return Decimal('0')
            
        gold_balance = user.gold_account.balance
        bonus_rate = self.bonus_rates.get(user.noble_rank.rank_name, Decimal('0'))
        return gold_balance * bonus_rate
    
    def distribute_monthly_bonus(self) -> Dict[int, Decimal]:
        """Distribute monthly bonus to all noble users"""
        noble_users = User.query.join(NobleRank).all()
        distribution_results = {}
        
        for user in noble_users:
            try:
                bonus_amount = self.calculate_user_bonus(user)
                if bonus_amount > 0:
                    user.gold_account.balance += bonus_amount
                    distribution_results[user.id] = bonus_amount
                    logger.info(f"Bonus distributed to user {user.id}: {bonus_amount}")
                    
            except Exception as e:
                logger.error(f"Error distributing bonus to user {user.id}: {str(e)}")
                continue
                
        db.session.commit()
        return distribution_results
    
    def get_bonus_statistics(self) -> Dict:
        """Get statistics about bonus distribution"""
        total_distributed = Decimal('0')
        distribution_by_rank = {}
        
        noble_users = User.query.join(NobleRank).all()
        for user in noble_users:
            bonus = self.calculate_user_bonus(user)
            rank_name = user.noble_rank.rank_name
            
            if rank_name not in distribution_by_rank:
                distribution_by_rank[rank_name] = {
                    'count': 0,
                    'total_bonus': Decimal('0')
                }
                
            distribution_by_rank[rank_name]['count'] += 1
            distribution_by_rank[rank_name]['total_bonus'] += bonus
            total_distributed += bonus
            
        return {
            'total_distributed': float(total_distributed),
            'distribution_by_rank': {
                rank: {
                    'count': stats['count'],
                    'total_bonus': float(stats['total_bonus'])
                }
                for rank, stats in distribution_by_rank.items()
            }
        }
