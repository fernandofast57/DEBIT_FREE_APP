
from app.models.models import User, db
from app.models.noble_system import NobleRank
from app.services.blockchain_service import BlockchainService
from app.utils.logging_config import get_logger
from typing import Dict, Any

logger = get_logger(__name__)

class NobleRankService:
    def __init__(self):
        self.blockchain_service = BlockchainService()
        
    async def validate_rank_transition(self, user_id: int, new_rank_id: int) -> Dict[str, Any]:
        """Validate rank transition according to glossary definitions"""
        try:
            user = await User.query.get(user_id)
            if not user:
                return {'status': 'rejected', 'message': 'User not found'}
                
            noble_rank = await NobleRank.query.get(new_rank_id)
            if not noble_rank:
                return {'status': 'rejected', 'message': 'Invalid noble rank'}
                
            # Check minimum investment requirements
            if user.total_investment < noble_rank.min_investment:
                return {
                    'status': 'rejected', 
                    'message': 'Investment requirements not met'
                }
                
            return {'status': 'verified', 'message': 'Rank transition validated'}
            
        except Exception as e:
            logger.error(f"Rank validation error: {str(e)}")
            return {'status': 'rejected', 'message': str(e)}
            
    async def update_user_rank(self, user_id: int, new_rank_id: int) -> Dict[str, Any]:
        """Update user noble rank with validation"""
        try:
            validation = await self.validate_rank_transition(user_id, new_rank_id)
            if validation['status'] != 'verified':
                return validation
                
            user = await User.query.get(user_id)
            user.noble_rank_id = new_rank_id
            
            # Update blockchain status
            if user.blockchain_address:
                await self.blockchain_service.update_noble_rank(
                    user.blockchain_address,
                    new_rank_id
                )
            
            await db.session.commit()
            logger.info(f"Updated rank for user {user_id} to {new_rank_id}")
            return {'status': 'verified', 'message': 'Rank updated successfully'}
            
        except Exception as e:
            await db.session.rollback()
            logger.error(f"Failed to update user rank: {str(e)}")
            return {'status': 'rejected', 'message': str(e)}
def generate_network_report(self, noble_id: int):
    """Generate detailed network performance report"""
    affiliates = self.get_network_affiliates(noble_id)
    total_volume = sum(a.transaction_volume for a in affiliates)
    network_growth = len([a for a in affiliates if a.created_at.month == datetime.now().month])
    
    return {
        "total_affiliates": len(affiliates),
        "monthly_growth": network_growth,
        "total_volume": total_volume,
        "performance_score": calculate_performance_score(total_volume, network_growth)
    }
from decimal import Decimal
from app.models.models import User, NobleRank, Transaction
from app.database import db

class NobleRankService:
    RANK_THRESHOLDS = {
        'Knight': Decimal('100'),
        'Baron': Decimal('500'),
        'Count': Decimal('1000'),
        'Duke': Decimal('5000'),
        'King': Decimal('10000')
    }
    
    async def update_user_rank(self, user_id: int):
        user = await User.query.get(user_id)
        total_gold = user.gold_account.balance
        
        for rank, threshold in self.RANK_THRESHOLDS.items():
            if total_gold >= threshold:
                user.noble_rank = rank
                break
                
        await db.session.commit()
