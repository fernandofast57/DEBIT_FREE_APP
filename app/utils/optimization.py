import os
import logging
from logging.handlers import RotatingFileHandler
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import time
from app.utils.logging_config import get_logger
from app import db

logger = get_logger(__name__)
cache = Cache(config={'CACHE_TYPE': 'simple'})

def setup_optimization(app):
    """Configure optimization settings for the application"""
    # Setup enhanced logging
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    file_handler = RotatingFileHandler(
        'logs/performance.log',
        maxBytes=10000000,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    logger.addHandler(file_handler)
    
    # Setup rate limiting
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    
    # Initialize caching
    cache.init_app(app)
    
    return app

def optimize_query(model, filters=None):
    """Optimize database queries using joins and eager loading"""
    query = db.session.query(model)
    if hasattr(model, 'user'):
        query = query.join(model.user)
    if filters:
        query = query.filter_by(**filters)
    return query
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from app import db

def optimize_queries():
    """Optimize database queries"""
    from sqlalchemy import text, inspect
    
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    # Only create indexes if tables exist
    with db.engine.connect() as conn:
        if 'accounting_entries' in tables:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_accounting_entries_user ON accounting_entries(user_id);
                CREATE INDEX IF NOT EXISTS idx_accounting_entries_date ON accounting_entries(entry_date);
            """))
        if 'noble_ranks' in tables:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_noble_ranks_level_status ON noble_ranks(level, status);
            """))
        if 'transformations' in tables:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_transformations_date ON transformations(transformation_date);
            """))
        conn.commit()

def create_indexes():
    """Create indexes for better query performance"""
    with db.engine.connect() as conn:
        # Check if tables exist before creating indexes
        tables = db.engine.table_names()
        
        if 'accounting_entries' in tables:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_accounting_entries_user ON accounting_entries(user_id);
                CREATE INDEX IF NOT EXISTS idx_accounting_entries_date ON accounting_entries(entry_date);
            """))
        
        if 'noble_ranks' in tables:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_noble_ranks_level_status ON noble_ranks(level, status);
            """))
        
        if 'transformations' in tables:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_transformations_date ON transformations(transformation_date);
            """))

    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())

    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - conn.info['query_start_time'].pop()
        if total > 0.2:  # Log slow queries (>200ms)
            logger.warning(f"Slow query detected: {statement[:100]}... ({total:.2f}s)")