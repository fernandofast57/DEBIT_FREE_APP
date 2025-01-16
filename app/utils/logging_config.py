
import logging
from logging.handlers import RotatingFileHandler
import os

APP_NAME = 'GoldInvestment'

def setup_logging():
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Configure the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create handlers
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=1024 * 1024,  # 1MB
        backupCount=10
    )
    console_handler = logging.StreamHandler()

    # Create formatters and add it to handlers
    log_format = '%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s'
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name (str): Name for the logger, usually __name__ of the module

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(f"{APP_NAME}.{name}")

    if not logger.handlers:  # Avoid adding handlers multiple times
        setup_logging()

    return logger

# Setup logging when module is imported
setup_logging()