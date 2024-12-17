
import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask

def setup_logging(app: Flask) -> None:
    """Setup logging configuration for the application"""
    if not os.path.exists('logs'):
        os.mkdir('logs')
        
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10240,
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    # Also log to console in development
    if not os.environ.get('PRODUCTION'):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        app.logger.addHandler(console_handler)
