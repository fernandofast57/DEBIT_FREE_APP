import logging
from logging.handlers import RotatingFileHandler
import os

APP_NAME = 'gold-investment'

def setup_logging(app):
    """Imposta la configurazione principale dei log dell'applicazione."""
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Log principale
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=102400,
        backupCount=10
    )
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    # Log di sicurezza
    security_handler = RotatingFileHandler(
        'logs/security.log',
        maxBytes=102400,
        backupCount=5
    )
    security_handler.setFormatter(formatter)
    security_handler.setLevel(logging.WARNING)
    app.logger.addHandler(security_handler)

def get_logger(name: str) -> logging.Logger:
    """Restituisce un logger personalizzato per un modulo specifico."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = RotatingFileHandler(
            f'logs/{name}.log',
            maxBytes=102400,
            backupCount=5
        )
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
