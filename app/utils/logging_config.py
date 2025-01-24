import logging
from logging.handlers import RotatingFileHandler
import os

APP_NAME = 'GoldInvestment'

# Create and configure the root logger
logger = logging.getLogger(APP_NAME)

def setup_logging():
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Configure the root logger
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

    # Add handlers to the logger if they haven't been added already
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

def get_logger(name="GoldInvestment"):
    """
    Get a logger instance with the specified name.

    Args:
        name (str): Name for the logger, usually __name__ of the module

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)

class GlossaryComplianceLogger:
    def __init__(self):
        self.logger = get_logger('glossary_compliance')

    def log_validation(self, component: str, results: dict):
        """Log validation results for a component"""
        status = 'PASS' if all(results.values()) else 'FAIL'
        self.logger.info(f"Component: {component} - Status: {status}")
        for check, result in results.items():
            self.logger.debug(f"{component}.{check}: {'PASS' if result else 'FAIL'}")

# Setup logging when module is imported
setup_logging()