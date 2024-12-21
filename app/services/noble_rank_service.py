
from app.models.models import User, NobleRank, db
from app.services.blockchain_service import BlockchainService
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

class NobleRankService:
    def __init__(self):
        self.blockchain_service = BlockchainService()
        
    async def update_user_rank(self, user_id: int, new_rank_id: int):
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
                
            noble_rank = NobleRank.query.get(new_rank_id)
            if not noble_rank:
                raise ValueError(f"Noble rank {new_rank_id} not found")
                
            user.noble_rank_id = new_rank_id
            
            # Update blockchain
            if user.blockchain_address:
                await self.blockchain_service.update_noble_rank(
                    user.blockchain_address,
                    new_rank_id
                )
            
            db.session.commit()
            logger.info(f"Updated rank for user {user_id} to {noble_rank.title}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update user rank: {str(e)}")
            raise
