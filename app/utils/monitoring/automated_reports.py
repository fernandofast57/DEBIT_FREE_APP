import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from app.models.models import Transaction, User
from app.utils.analytics.user_analytics import AnalisiUtente

logger = logging.getLogger(__name__)

class AutomatedReportGenerator:
    def __init__(self):
        self.report_history = []
        self.report_types = {
            'daily': 24 * 60 * 60,
            'weekly': 7 * 24 * 60 * 60,
            'monthly': 30 * 24 * 60 * 60
        }

    def generate_system_report(self) -> Dict[str, Any]:
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'system_status': 'healthy',
            'metrics': {}
        }
        self.report_history.append(report)
        return report

    def get_report_history(self) -> List[Dict[str, Any]]:
        return self.report_history

class AutomatedReports:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.report_generator = AutomatedReportGenerator() # Added instance of the new class

    async def generate_daily_report(self) -> Dict:
        today = datetime.utcnow().date()
        report = {
            'date': today.isoformat(),
            'transactions': await self._get_daily_transactions(),
            'system_metrics': await self._get_system_metrics()
        }
        self.report_generator.generate_system_report() #Calling the new report generation method
        return report

    async def _get_daily_transactions(self) -> Dict:
        today = datetime.utcnow().date()
        transactions = await Transaction.query.filter(
            Transaction.date >= today
        ).all()
        return {
            'total': len(transactions),
            'total_volume': sum(t.amount for t in transactions),
            'status_counts': self._count_transaction_status(transactions)
        }

    async def _get_system_metrics(self) -> Dict:
        return {
            'active_users': await User.query.filter(
                User.last_login >= datetime.utcnow() - timedelta(days=1)
            ).count(),
            'performance': await AnalisiUtente.get_performance_metrics()
        }

    def _count_transaction_status(self, transactions: List[Transaction]) -> Dict[str, int]:
        status_counts = {}
        for transaction in transactions:
            status = transaction.status
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts