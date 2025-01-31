import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
from decimal import Decimal
from sqlalchemy import func
from app.models.models import GoldAccount, User
from app.models.transaction import Transaction
from app.models.noble_system import NobleRank

class AnalyticsService:
    def __init__(self, db_session):
        self.db = db_session

    async def get_system_metrics(self) -> Dict:
        """Raccoglie metriche chiave del sistema"""
        total_users = await self.db.query(User).count()
        total_gold = await self.db.query(func.sum(GoldAccount.balance)).scalar() or Decimal('0')
        total_transactions = await self.db.query(Transaction).count()

        return {
            "total_users": total_users,
            "total_gold": float(total_gold),
            "total_transactions": total_transactions,
            "avg_gold_per_user": float(total_gold / total_users) if total_users > 0 else 0
        }

    async def get_noble_distribution(self) -> Dict:
        """Analizza distribuzione ranghi nobiliari"""
        ranks = await self.db.query(
            NobleRank.level,
            func.count(User.id)
        ).join(User).group_by(NobleRank.level).all()

        return {level: count for level, count in ranks}

    async def get_transaction_trends(self, days: int = 30) -> List:
        """Analizza trend transazioni"""
        start_date = datetime.utcnow() - timedelta(days=days)
        transactions = await self.db.query(
            func.date(Transaction.timestamp),
            func.count(Transaction.id)
        ).filter(Transaction.timestamp >= start_date)\
         .group_by(func.date(Transaction.timestamp)).all()

        return [{"date": date, "count": count} for date, count in transactions]