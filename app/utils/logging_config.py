
import os
import logging
from datetime import datetime
from typing import Dict, Any
from logging.handlers import RotatingFileHandler

APP_NAME = 'gold-investment'

def setup_logging():
    """Initialize base logging configuration"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logger = logging.getLogger(APP_NAME)
    
    # Only add handler if it doesn't exist
    if not logger.handlers:
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
    """Get or create a logger with the given name"""
    logger = logging.getLogger(name)
    
    # Only add handler if it doesn't exist
    if not logger.handlers:
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        handler = RotatingFileHandler(
            f'logs/{name.replace(".", "_")}.log',
            maxBytes=10000000,
            backupCount=5
        )
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
    
    return logger

class GlossaryComplianceLogger:
    def __init__(self, app_name: str = APP_NAME):
        self.logger = get_logger(f'{app_name}_compliance')
    
    def log_validation(self, component: str, validation_result: Dict[str, Any]):
        """Log validation results"""
        self.logger.info(
            f"Component: {component} - "
            f"Status: {'compliant' if all(validation_result.values()) else 'non-compliant'} - "
            f"Timestamp: {datetime.utcnow().isoformat()}"
        )
        
        for key, value in validation_result.items():
            if not value:
                self.logger.warning(
                    f"Non-compliant item found - "
                    f"Component: {component} - "
                    f"Item: {key}"
                )

    def log_compliance_check(self, item: str, is_compliant: bool):
        """Log individual compliance checks"""
        level = logging.INFO if is_compliant else logging.WARNING
        self.logger.log(
            level,
            f"Compliance check - Item: {item} - "
            f"Status: {'compliant' if is_compliant else 'non-compliant'}"
        )
