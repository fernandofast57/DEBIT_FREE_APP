
import logging
from logging.handlers import RotatingFileHandler

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    handler = RotatingFileHandler('logs/app.log', maxBytes=10000000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger

def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        if not os.path.exists('logs'):
            os.makedirs('logs')
        handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10000000,
            backupCount=5
        )
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def setup_blockchain_logging():
    logger = logging.getLogger('blockchain')
    logger.setLevel(logging.INFO)
    
    handler = RotatingFileHandler('logs/blockchain.log', maxBytes=10000000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
