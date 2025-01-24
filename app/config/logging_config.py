
import os
import logging
from logging.handlers import RotatingFileHandler

LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logging():
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    handlers = {
        'app': RotatingFileHandler(f'{LOG_DIR}/app.log', maxBytes=10485760, backupCount=5),
        'error': RotatingFileHandler(f'{LOG_DIR}/error.log', maxBytes=10485760, backupCount=5),
        'audit': RotatingFileHandler(f'{LOG_DIR}/audit.log', maxBytes=10485760, backupCount=5),
        'security': RotatingFileHandler(f'{LOG_DIR}/security.log', maxBytes=10485760, backupCount=5)
    }

    for handler in handlers.values():
        handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    for handler in handlers.values():
        root_logger.addHandler(handler)

    return handlers
