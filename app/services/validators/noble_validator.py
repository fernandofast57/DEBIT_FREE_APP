from decimal import Decimal
from app.models.noble_system import NobleRank
from app.utils.logging_config import logger

class NobleValidator:
    NOBLE_RANK_MINIMUM = 'Knight'
    NOBLE_RANK_THRESHOLDS = {
        'Knight': 0,
        'Baron': 50000,
        'Count': 100000,
        'Duke': 250000
    }
    @staticmethod
    async def validate_rank_upgrade(user_id: int, new_rank_id: int) -> bool:
        try:
            current_rank = await NobleRank.query.filter_by(user_id=user_id).first()
            new_rank = await NobleRank.query.get(new_rank_id)

            if not new_rank:
                logger.error(f"Invalid rank ID: {new_rank_id}")
                return False

            if current_rank and current_rank.level >= new_rank.level:
                logger.error(f"Invalid rank upgrade: current={current_rank.level}, new={new_rank.level}")
                return False

            return True
        except Exception as e:
            logger.error(f"Rank validation error: {str(e)}")
            return False