from decimal import Decimal
from typing import Optional, Dict, Any
from app.models import db, NobleRank, NobleRelation, User
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

class NobleRankService:
    """Service for managing noble ranks and bonuses as per glossary"""

    def __init__(self, db_session):
        self.db = db_session

    async def calculate_noble_bonus(self, user_id: int, transaction_amount: Decimal) -> Decimal:
        """Calculate noble bonus based on rank and transaction amount"""
        user = await self.db.query(User).get(user_id)
        if not user or not hasattr(user, 'noble_relation'):
            return Decimal('0')

        noble_rank = await self.db.query(NobleRank).get(user.noble_relation.noble_rank_id)
        if not noble_rank:
            return Decimal('0')

        return transaction_amount * noble_rank.bonus_rate

    async def verify_noble_status(self, user_id: int) -> bool:
        """Verify noble status according to glossary requirements"""
        noble_relation = await self.db.query(NobleRelation).filter_by(user_id=user_id).first()
        return noble_relation is not None and noble_relation.verification_status == 'verified'

    async def update_user_rank(self, user_id: int, new_rank_id: int) -> Dict[str, Any]:
        """Update user noble rank with validation"""
        try:
            user = await self.db.query(User).get(user_id)
            if not user:
                return {'status': 'rejected', 'message': 'User not found'}

            user.noble_rank_id = new_rank_id

            await self.db.commit()
            return {'status': 'verified', 'message': 'Rank updated successfully'}

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update user rank: {str(e)}")
            return {'status': 'rejected', 'message': str(e)}

    async def verify_rank(self, user_id: int, noble_status: str) -> Dict[str, str]:
        if noble_status not in ['to_be_verified', 'verified', 'rejected']:
            return {'status': 'error', 'message': 'Invalid noble status'}

        user = await self.db.get(User, user_id)
        if not user:
            return {'status': 'rejected', 'message': 'User not found'}

        noble_relation = NobleRelation(
            user_id=user_id,
            status=noble_status
        )
        self.db.add(noble_relation)
        await self.db.commit()

        return {'status': 'verified', 'message': 'Noble rank verified successfully'}