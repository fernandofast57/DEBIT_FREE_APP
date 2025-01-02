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
    """Create optimized database indexes"""
    try:
        with db.engine.connect() as conn:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);
                CREATE INDEX IF NOT EXISTS idx_transformations_date ON transformations(created_at);
                CREATE INDEX IF NOT EXISTS idx_noble_ranks_level ON noble_ranks(level);
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
                CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
                CREATE INDEX IF NOT EXISTS idx_noble_relations_user_id ON noble_relations(user_id);
            """))
        db.session.commit()
        print("Database optimization completed successfully")
    except Exception as e:
        print(f"Error creating indexes: {e}")
        db.session.rollback()