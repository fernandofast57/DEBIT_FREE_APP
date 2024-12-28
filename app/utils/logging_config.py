import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # File handler for all logs
    file_handler = RotatingFileHandler(
        'logs/app.log', maxBytes=10485760, backupCount=10
    )
    file_handler.setFormatter(formatter)

    # Error file handler
    error_handler = RotatingFileHandler(
        'logs/error.log', maxBytes=10485760, backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)

    return root_logger

logger = setup_logging()