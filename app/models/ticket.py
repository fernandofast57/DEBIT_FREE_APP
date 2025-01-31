from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class TicketStatus:
    OPEN = "open"
    IN_PROGRESS = "in progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default=TicketStatus.OPEN)
    priority = db.Column(db.String(20), default='medium')
    category = db.Column(db.String(50))
    subcategory = db.Column(db.String(50))
    keywords = db.Column(db.String(200))
    resolution = db.Column(db.Text)
    resolution_time = db.Column(db.Integer)  # Time in minutes
    satisfaction_rating = db.Column(db.Integer)
    ai_tags = db.Column(db.JSON)
    related_tickets = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)