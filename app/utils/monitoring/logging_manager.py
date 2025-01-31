import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

class GestoreLog:
    def __init__(self, log_file: str = 'app.log'):
        self.logger = logging.getLogger('app')
        self.handler: Optional[RotatingFileHandler] = None
        self.setup_logging(log_file)

    def setup_logging(self, log_file: str) -> None:
        self.handler = RotatingFileHandler(
            f'logs/{log_file}',
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)