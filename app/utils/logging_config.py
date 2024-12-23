
import logging
from datetime import datetime
from typing import Dict, Any

APP_NAME = 'gold-investment'

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

    def log_compliance_check(self, item: str, is_compliant: bool):
        """Log individual compliance checks"""
        level = logging.INFO if is_compliant else logging.WARNING
        self.logger.log(
            level,
            f"Compliance check - Item: {item} - "
            f"Status: {'compliant' if is_compliant else 'non-compliant'}"
        )
