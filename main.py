# main.py
from app import create_app
import logging
from logging.handlers import RotatingFileHandler
import os

app = create_app()

if __name__ == '__main__':
    app.logger.info('Gold Investment Platform startup')
    app.run(host='0.0.0.0', port=5000)