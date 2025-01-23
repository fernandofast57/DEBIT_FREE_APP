
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy import func
from app.models import User, Transaction, MoneyAccount, GoldAccount
from app.database import db

class UserAnalytics:
    @staticmethod
    async def get_user_metrics(user_id: int) -> Dict:
        """Analisi metriche utente"""
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        transactions = await db.session.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.created_at >= week_ago
        ).all()

        return {
            'total_transactions': len(transactions),
            'total_volume': sum(t.amount for t in transactions),
            'activity_score': len(transactions) * 10
        }

    @staticmethod
    async def get_performance_metrics(user_id: int) -> Dict:
        """Analisi performance investimenti"""
        user = await db.session.query(User).get(user_id)
        gold_account = user.gold_account
        money_account = user.money_account

        return {
            'gold_balance': gold_account.balance,
            'money_balance': money_account.balance,
            'total_value': gold_account.balance * 1800 + money_account.balance
        }
