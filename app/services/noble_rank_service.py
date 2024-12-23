
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
