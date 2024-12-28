
from flask_sqlalchemy import SQLAlchemy
from app import db
import logging
from time import time

def optimize_queries():
    """Apply database query optimizations"""
    db.session.execute('PRAGMA journal_mode=WAL')
    db.session.execute('PRAGMA synchronous=NORMAL')
    db.session.execute('PRAGMA cache_size=10000')
    db.session.commit()

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
