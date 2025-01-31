
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy import func
from app.models import User, Transaction, ContoEuro, ContoOro
from app.database import db

class UserAnalytics:
    @staticmethod
    async def get_user_metrics(user_id: int) -> Dict:
        """User metrics analysis according to glossary"""
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        transazioni = await db.session.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.created_at >= settimana_fa
        ).all()

        return {
            'totale_transazioni': len(transazioni),
            'volume_totale': sum(t.amount for t in transazioni),
            'punteggio_attivita': len(transazioni) * 10
        }

    @staticmethod
    async def get_metriche_performance(user_id: int) -> Dict:
        """Analisi performance investimenti secondo glossario"""
        utente = await db.session.query(User).get(user_id)
        conto_oro = utente.conto_oro
        conto_euro = utente.conto_euro

        return {
            'saldo_oro': conto_oro.balance,
            'saldo_euro': conto_euro.balance,
            'valore_totale': conto_oro.balance * 1800 + conto_euro.balance
        }
