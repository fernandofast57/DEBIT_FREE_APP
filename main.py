
import os
from flask import Flask
from flask_cors import CORS
from app import create_app
from app.config.constants import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app(Config())
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    with app.app_context():
        try:
            port = int(os.getenv('PORT', 8080))
            env = os.getenv('FLASK_ENV', 'development')
            debug = env == 'development'
            
            from app.utils.load_balancer import load_balancer
            server = load_balancer.get_next_server()
            
            logger.info(f"Starting application on {server['host']}:{server['port']} in {env} mode")
            app.run(host=server['host'], port=server['port'], debug=debug)
        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            raise
