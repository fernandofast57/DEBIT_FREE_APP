
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

APP_NAME = 'gold_investment'
logger = logging.getLogger(APP_NAME)

def get_logger(module_name=None):
    return logging.getLogger(module_name if module_name else APP_NAME)

def setup_logging():
    log_dir = 'logs'
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    error_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=10485760,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    info_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,
        backupCount=5
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(info_handler)

    return root_logger
