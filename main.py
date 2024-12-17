# main.py
from app import create_app
import logging
from logging.handlers import RotatingFileHandler
import os

app = create_app()

if __name__ == '__main__':
    app.logger.info('Gold Investment Platform startup')
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)