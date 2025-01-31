
from app.models import db, NobleRelation, User
from app.utils.logging_config import get_logger
from sqlalchemy import text, Index
from sqlalchemy.exc import IntegrityError
from typing import Optional, List

logger = get_logger(__name__)

class ReferralService:
    MAX_LEVEL = 3  # Maximum level for bonus calculations
    
    async def create_referral(self, referrer_id: int, referred_id: int) -> bool:
        """Create a new referral relationship and calculate levels
        
        Args:
            referrer_id: ID of the referring user
            referred_id: ID of the user being referred
            
        Returns:
            bool: True if referral was created successfully, False otherwise
        """
        try:
            if referrer_id == referred_id:
                logger.warning(f"Self-referral attempted: {referrer_id}")
                return False
                
            # Check if referral already exists
            existing = await NobleRelation.query.filter_by(
                referrer_id=referrer_id,
                referred_id=referred_id
            ).first()
            
            if existing:
                logger.info(f"Referral already exists: {referrer_id} -> {referred_id}")
                return False
            
            # Create direct referral
            relation = NobleRelation(
                referrer_id=referrer_id,
                referred_id=referred_id,
                level=1
            )
            db.session.add(relation)
            
            # Create indirect relations up to MAX_LEVEL
            await self._create_indirect_relations(referrer_id, referred_id)
            
            await db.session.commit()
            logger.info(f"Referral created successfully: {referrer_id} -> {referred_id}")
            return True
            
        except IntegrityError as e:
            logger.error(f"Database integrity error creating referral: {str(e)}")
            await db.session.rollback()
            return False
        except ValueError as e:
            logger.error(f"Invalid data error creating referral: {str(e)}")
            await db.session.rollback()
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating referral: {str(e)}")
            await db.session.rollback()
            return False
    
    async def _create_indirect_relations(self, original_referrer_id: int, new_user_id: int) -> None:
        """Create indirect referral relationships up to MAX_LEVEL using recursive CTE
        
        This method creates referral relationships between the new user and all upline
        referrers up to MAX_LEVEL deep in the referral tree. It uses a recursive CTE
        for efficient querying of the referral chain.
        
        Args:
            original_referrer_id: ID of the original referring user
            new_user_id: ID of the newly referred user
            
        Raises:
            IntegrityError: If there are database constraint violations
            ValueError: If invalid user IDs are provided
        """
        query = text("""
            WITH RECURSIVE upline AS (
                SELECT referrer_id, referred_id, 1 as level
                FROM noble_relations 
                WHERE referred_id = :referrer_id
                UNION ALL
                SELECT nr.referrer_id, nr.referred_id, upline.level + 1
                FROM noble_relations nr
                JOIN upline ON nr.referred_id = upline.referrer_id
                WHERE upline.level < :max_level
            )
            SELECT DISTINCT referrer_id, level + 1 as new_level
            FROM upline
            WHERE level + 1 <= :max_level
        """)
        
        try:
            result = await db.session.execute(
                query,
                {"referrer_id": original_referrer_id, "max_level": self.MAX_LEVEL}
            )
            
            for row in result:
                relation: NobleRelation = NobleRelation(
                    referrer_id=row.referrer_id,
                    referred_id=new_user_id,
                    level=row.new_level
                )
                db.session.add(relation)
                
        except Exception as e:
            logger.error(f"Error creating indirect relations: {str(e)}")
            raise

# Create index on referred_id for better query performance
Index('idx_noble_relations_referred_id', NobleRelation.__table__.c.referred_id)
