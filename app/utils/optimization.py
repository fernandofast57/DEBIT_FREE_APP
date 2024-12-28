
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
        # Check if required tables exist
        tables = ['users', 'transactions', 'noble_relations']
        existing_tables = {}
        
        for table in tables:
            result = db.session.execute(text(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
            ))
            existing_tables[table] = bool(result.fetchone())
        
        # Create indexes only for existing tables
        if existing_tables['users']:
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)'))
            print("Created index on users.email")
            
        if existing_tables['transactions']:
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)'))
            print("Created index on transactions.user_id")
            
        if existing_tables['noble_relations']:
            db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_noble_relations_user_id ON noble_relations(user_id)'))
            print("Created index on noble_relations.user_id")
            
        db.session.commit()
        print("Database optimization completed successfully")
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
