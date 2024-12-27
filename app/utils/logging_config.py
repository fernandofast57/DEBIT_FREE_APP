
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=102400,
        backupCount=10
    )
    
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    )
    
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    # Separate security log
    security_handler = RotatingFileHandler(
        'logs/security.log',
        maxBytes=102400,
        backupCount=5
    )
    security_handler.setFormatter(formatter)
    security_handler.setLevel(logging.WARNING)
    app.logger.addHandler(security_handler)
