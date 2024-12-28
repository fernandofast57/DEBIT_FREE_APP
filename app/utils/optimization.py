
from flask_sqlalchemy import SQLAlchemy
from app import db
import logging
from time import time
from sqlalchemy import text

def optimize_queries():
    """Apply database query optimizations"""
    db.session.execute(text('PRAGMA journal_mode=WAL'))
    db.session.execute(text('PRAGMA synchronous=NORMAL'))
    db.session.execute(text('PRAGMA cache_size=10000'))
    db.session.commit()

def create_indexes():
    """Create database indexes for better query performance"""
    try:
        db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)'))
        db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)'))
        db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_noble_relations_user_id ON noble_relations(user_id)'))
        db.session.commit()
        print("Database indexes created successfully")
    except Exception as e:
        print(f"Error creating indexes: {e}")
        db.session.rollback()

def optimize_query(model, filters=None, limit=100):
    """Optimize database queries using SQLAlchemy"""
    query = db.session.query(model)
    if hasattr(model, 'user'):
        query = query.join(model.user)
    if filters:
        query = query.filter_by(**filters)
    return query.limit(limit)

def performance_monitor(func):
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        duration = time() - start_time
        logging.info(f"{func.__name__} took {duration:.2f} seconds")
        return result
    return wrapper
