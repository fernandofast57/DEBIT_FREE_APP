
from decimal import Decimal, ROUND_DOWN
from typing import Optional, Dict, Any
from app.models import db, NobleRank, NobleRelation, User
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

class NobleService: 
    def __init__(self, db_session):
        self.db = db_session

    async def calcola_bonus_nobile(self, user_id: int, gold_weight: Decimal) -> Dict[str, Any]:
        try:
            user = await self.db.query(User).get(user_id)
            if not user or not hasattr(user, 'noble_relation'):
                return {"bonus": Decimal('0'), "status": "no_noble_rank"}

            level = user.noble_relation.level
            premio_referral = {
                1: Decimal('0.007'),  # 0.7% in grammi dell'oro acquisito
                2: Decimal('0.005'),  # 0.5% in grammi dell'oro acquisito
                3: Decimal('0.005')   # 0.5% in grammi dell'oro acquisito
            }

            bonus = (gold_weight * premio_referral.get(level, Decimal('0'))).quantize(Decimal('0.0001'))

            return {
                "bonus": bonus,
                "status": "calculated",
                "level": level,
                "percentage": premio_referral.get(level, Decimal('0')) * 100
            }
        except Exception as e:
            logger.error(f"Errore nel calcolo del bonus nobile: {str(e)}")
            return {"bonus": Decimal('0'), "status": "error"}

    async def verifica_stato_nobile(self, user_id: int) -> bool: 
        """Verifica lo stato del rango nobile"""
        noble_relation = await self.db.query(NobleRelation).filter_by(user_id=user_id).first()
        return noble_relation is not None and noble_relation.verification_status == 'verified'

    async def aggiorna_rango_utente(self, user_id: int, new_rank_id: int) -> Dict[str, Any]: 
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

    async def verifica_rango(self, user_id: int, noble_status: str) -> Dict[str, str]: 
        if noble_status not in ['in_verifica', 'verificato', 'respinto']:
            return {'status': 'errore', 'message': 'Stato RangoNobile non valido'}

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
