
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    """Configure enhanced logging system"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    # Main application logger
    main_logger = logging.getLogger('app')
    main_logger.setLevel(logging.INFO)
    
    # File handler with rotation
    handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10000000,  # 10MB
        backupCount=10
    )
    
    # Detailed formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]'
    )
    handler.setFormatter(formatter)
    main_logger.addHandler(handler)
    
    # Also log validation errors
    validation_logger = logging.getLogger('validation')
    validation_logger.setLevel(logging.WARNING)
    validation_handler = RotatingFileHandler(
        'logs/validation.log',
        maxBytes=5000000,  # 5MB
        backupCount=5
    )
    validation_handler.setFormatter(formatter)
    validation_logger.addHandler(validation_handler)
    
    return main_logger, validation_logger
def setup_blockchain_logging():
    logger = logging.getLogger('blockchain')
    logger.setLevel(logging.INFO)
    
    handler = RotatingFileHandler('logs/blockchain.log', maxBytes=10000000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
