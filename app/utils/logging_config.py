import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Configure log handlers with rotation
    handlers = {
        'app': RotatingFileHandler('logs/app.log', maxBytes=1024*1024, backupCount=10),
        'error': RotatingFileHandler('logs/error.log', maxBytes=1024*1024, backupCount=10),
        'security': RotatingFileHandler('logs/security.log', maxBytes=1024*1024, backupCount=10),
        'performance': RotatingFileHandler('logs/performance.log', maxBytes=1024*1024, backupCount=5),
        'audit': RotatingFileHandler('logs/audit.log', maxBytes=1024*1024, backupCount=30)
    }

    # Configure formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Apply formatter to all handlers
    for handler in handlers.values():
        handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    for handler in handlers.values():
        root_logger.addHandler(handler)

    return handlers

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