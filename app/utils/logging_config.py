
import os
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('gold-investment')

def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10000000,
        backupCount=5
    )
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger

# Initialize logger
setup_logging()

__all__ = ['logger', 'setup_logging']
