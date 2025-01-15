# app/utils/logging_config.py
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import has_request_context, request


class RequestFormatter(logging.Formatter):

    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)


def setup_logging(app):
    """Configura il logging per l'ambiente di produzione"""

    # Crea la directory dei log se non esiste
    if not os.path.exists('logs'):
        os.mkdir('logs')

    # Configura il formatter con informazioni aggiuntive
    formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s')

    # File handler per errori
    error_file_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=10485760,  # 10MB
        backupCount=10)
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)

    # File handler per info
    info_file_handler = RotatingFileHandler(
        'logs/info.log',
        maxBytes=10485760,  # 10MB
        backupCount=10)
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(formatter)

    # Rimuovi gli handler esistenti
    app.logger.handlers = []

    # Aggiungi i nuovi handler
    app.logger.addHandler(error_file_handler)
    app.logger.addHandler(info_file_handler)

    # Imposta il livello di logging base
    app.logger.setLevel(logging.INFO)

    # Log iniziale
    app.logger.info('Logging setup completed')
