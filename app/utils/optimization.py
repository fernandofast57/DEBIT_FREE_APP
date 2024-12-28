
from flask_sqlalchemy import SQLAlchemy
from app import db
import logging
from time import time
from sqlalchemy import text

class OptimizationService:
    def __init__(self):
        self.db = db

    def optimize_query(self, model, filters=None):
        query = self.db.session.query(model)
        if filters:
            query = query.filter_by(**filters)
        return query

    def bulk_insert(self, objects):
        try:
            self.db.session.bulk_save_objects(objects)
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e

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
