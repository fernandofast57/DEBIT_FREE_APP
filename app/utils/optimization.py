
import os
import logging
from logging.handlers import RotatingFileHandler
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
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
