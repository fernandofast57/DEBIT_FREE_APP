# main.py
import os
import logging
from logging.config import dictConfig
from flask import Flask
from flask_cors import CORS
from app import create_app
from app.config.settings import Config
from app.utils.monitoring.performance_monitor import PerformanceMonitor
from app.utils.security.circuit_breaker import CircuitBreaker
import signal
import resource

# Configurazione logging avanzata
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {
            'format':
            '[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/gold_app.log',
            'maxBytes': 10485760,
            'backupCount': 10,
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
}

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


class ApplicationManager:

    def __init__(self):
        self.app = None
        self.performance_monitor = PerformanceMonitor()

    def initialize_app(self):
        """Inizializza l'applicazione Flask con le tue configurazioni esistenti"""
        self.app = create_app(Config())
        CORS(self.app, resources={r"/api/*": {"origins": "*"}})

        @self.app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Headers',
                                 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods',
                                 'GET,PUT,POST,DELETE,OPTIONS')
            return response

        return self.app

    def setup_signal_handlers(self):

        def handle_shutdown(signum, frame):
            logger.info(f"Received shutdown signal. Performing cleanup...")
            self.performance_monitor.save_metrics()

        signal.signal(signal.SIGTERM, handle_shutdown)
        signal.signal(signal.SIGINT, handle_shutdown)

    def run(self):
        try:
            self.app = self.initialize_app()
            self.setup_signal_handlers()

            port = int(os.getenv('PORT', 8080))
            env = os.getenv('FLASK_ENV', 'development')
            debug = False
            use_reloader = False

            server = {'host': '0.0.0.0', 'port': 8080}  # Default server config

            logger.info(
                f"Starting application on {server['host']}:{server['port']} in production mode"
            )

            with self.app.app_context():
                # Use Gunicorn for production
                from gunicorn.app.base import BaseApplication

            class StandaloneApplication(BaseApplication):
                def __init__(self, app, options=None):
                    self.options = options or {}
                    self.application = app
                    super().__init__()

                def load_config(self):
                    for key, value in self.options.items():
                        self.cfg.set(key, value)

                def load(self):
                    return self.application

            options = {
                'bind': f"0.0.0.0:{server['port']}",
                'workers': 4,
                'worker_class': 'sync',
                'timeout': 30
            }

            StandaloneApplication(self.app, options).run()

        except Exception as e:
            logger.error(f"Failed to start application: {str(e)}", exc_info=True)
            raise SystemExit(1)
        finally:
            self.performance_monitor.save_metrics()


if __name__ == '__main__':
    application = ApplicationManager()
    application.run()
