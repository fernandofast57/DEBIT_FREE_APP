
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional
from app.database import db
from app.models.weekly_amount import WeeklyAmount
from app.utils.audit_logger import audit_logger

class WeeklyAmountService:
    @staticmethod
    async def record_amount(user_id: int, amount: Decimal) -> Dict:
        """Record a new weekly amount"""
        try:
            now = datetime.utcnow()
            week_start = now - timedelta(days=now.weekday())
            week_end = week_start + timedelta(days=6)
            
            existing = await WeeklyAmount.query.filter(
                WeeklyAmount.user_id == user_id,
                WeeklyAmount.week_start <= now,
                WeeklyAmount.week_end >= now
            ).first()
            
            if existing:
                existing.amount += amount
                await db.session.commit()
                entry_id = existing.id
            else:
                entry = WeeklyAmount(
                    user_id=user_id,
                    amount=amount,
                    week_start=week_start,
                    week_end=week_end
                )
                db.session.add(entry)
                await db.session.commit()
                entry_id = entry.id
            
            audit_logger.info(f"Recorded weekly amount {amount} for user {user_id}")
            return {"status": "success", "entry_id": entry_id}

        except Exception as e:
            await db.session.rollback()
            audit_logger.error(f"Failed to record weekly amount: {str(e)}")
            return {"status": "error", "message": str(e)}

    @staticmethod
    async def get_user_weekly_total(user_id: int) -> Optional[Decimal]:
        """Get total amount for current week"""
        try:
            now = datetime.utcnow()
            amount = await WeeklyAmount.query.filter(
                WeeklyAmount.user_id == user_id,
                WeeklyAmount.week_start <= now,
                WeeklyAmount.week_end >= now
            ).with_entities(WeeklyAmount.amount).scalar()
            
            return amount or Decimal('0')
        except Exception as e:
            audit_logger.error(f"Error getting weekly total: {str(e)}")
            return None

    @staticmethod
    async def get_pending_amounts() -> List[WeeklyAmount]:
        """Get all unprocessed weekly amounts"""
        return await WeeklyAmount.query.filter_by(processed=False).all()

    @staticmethod
    async def mark_as_processed(entry_id: int) -> bool:
        """Mark a weekly amount as processed"""
        try:
            entry = await WeeklyAmount.query.get(entry_id)
            if entry:
                entry.processed = True
                await db.session.commit()
                return True
            return False
        except Exception as e:
            await db.session.rollback()
            audit_logger.error(f"Error marking amount as processed: {str(e)}")
            return False
