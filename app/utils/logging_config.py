
import os
import logging
from logging.handlers import RotatingFileHandler

APP_NAME = 'gold-investment'
logger = logging.getLogger(APP_NAME)

def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10000000,
        backupCount=5
    )
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Restituisce un logger con un nome specifico.
    """
    custom_logger = logging.getLogger(name)
    if not custom_logger.handlers:
        handler = RotatingFileHandler(
            f'logs/{name}.log',
            maxBytes=10000000,
            backupCount=5
        )
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        custom_logger.setLevel(logging.INFO)
        custom_logger.addHandler(handler)
    return custom_logger

# Initialize logger
setup_logging()

__all__ = ['logger', 'setup_logging', 'get_logger']
import logging
from datetime import datetime
from typing import Dict, Any

class GlossaryComplianceLogger:
    def __init__(self, app_name: str = 'gold-investment'):
        self.logger = logging.getLogger(f'{app_name}_compliance')
        handler = logging.FileHandler('logs/glossary_compliance.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_validation(self, component: str, validation_result: Dict[str, Any]):
        """Log component validation results"""
        self.logger.info(
            f"Component: {component} - "
            f"Status: {'compliant' if all(validation_result.values()) else 'non-compliant'} - "
            f"Timestamp: {datetime.utcnow().isoformat()}"
        )
        
        # Log specific validation failures
        for key, value in validation_result.items():
            if not value:
                self.logger.warning(
                    f"Non-compliant item found - "
                    f"Component: {component} - "
                    f"Item: {key}"
                )
