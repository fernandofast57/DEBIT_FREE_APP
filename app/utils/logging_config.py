
import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging():
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Main application log
    app_handler = logging.handlers.RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    app_handler.setFormatter(formatter)
    app_handler.setLevel(logging.INFO)

    # Security events log
    security_handler = logging.handlers.RotatingFileHandler(
        'logs/security.log',
        maxBytes=10485760,
        backupCount=10
    )
    security_handler.setFormatter(formatter)
    security_handler.setLevel(logging.WARNING)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(security_handler)

    return root_logger
