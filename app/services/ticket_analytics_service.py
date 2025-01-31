
from datetime import datetime, timedelta
from sqlalchemy import func
from app.models.ticket import Ticket
from app.database import db

class TicketAnalyticsService:
    @staticmethod
    async def analyze_common_issues():
        """Analyze most common ticket categories and their resolutions"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        return await db.session.query(
            Ticket.category,
            func.count(Ticket.id).label('count'),
            func.avg(Ticket.resolution_time).label('avg_resolution_time')
        ).filter(Ticket.created_at >= thirty_days_ago).group_by(Ticket.category).all()

    @staticmethod
    async def get_ai_training_data():
        """Get structured data for AI training"""
        tickets = await db.session.query(Ticket).filter(
            Ticket.resolution.isnot(None)
        ).order_by(Ticket.satisfaction_rating.desc()).limit(1000).all()
        
        return [{
            'issue': ticket.description,
            'resolution': ticket.resolution,
            'category': ticket.category,
            'keywords': ticket.keywords,
            'success_rating': ticket.satisfaction_rating
        } for ticket in tickets]

    @staticmethod
    async def update_ai_tags(ticket_id: int, tags: dict):
        """Update AI-generated tags for a ticket"""
        ticket = await db.session.query(Ticket).get(ticket_id)
        if ticket:
            ticket.ai_tags = tags
            await db.session.commit()
            return True
        return False
