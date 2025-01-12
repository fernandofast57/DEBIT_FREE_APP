import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

APP_NAME = 'gold_investment'
logger = logging.getLogger(APP_NAME)

def get_logger(module_name=None):
    return logging.getLogger(module_name if module_name else APP_NAME)

def setup_logging():
    logger = get_logger()
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger