import os
import logging
import sys
from logging.config import dictConfig
from flask import Flask
from flask_cors import CORS
from app import create_app
from app.config.settings import Config
from app.utils.monitoring.performance_monitor import SystemPerformanceMonitor

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] %(message)s',
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
        self.performance_monitor = SystemPerformanceMonitor()

    def initialize_app(self):
        """Initialize Flask application with configurations"""
        self.app = create_app(Config())
        CORS(self.app, resources={r"/api/*": {"origins": "*"}})

        @self.app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response

        return self.app

    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        def handle_shutdown(signum, frame):
            logger.info(f"Received shutdown signal {signum}. Performing cleanup...")
            self.performance_monitor.save_metrics()
            sys.exit(0)

        import signal
        signal.signal(signal.SIGTERM, handle_shutdown)
        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGQUIT, handle_shutdown)

    def run(self):
        """Run the application"""
        try:
            self.app = self.initialize_app()
            self.setup_signal_handlers()

            server = {'host': '0.0.0.0', 'port': int(os.getenv('PORT', 8080))}
            logger.info(f"Starting application on {server['host']}:{server['port']} in production mode")

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
                'bind': f"{server['host']}:{server['port']}",
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
    try:
        application = ApplicationManager()
        application.run()
    except Exception as e:
        logging.error(f"Application startup error: {str(e)}", exc_info=True)
        sys.exit(1)