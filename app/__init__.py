# app/__init__.py
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os

db = SQLAlchemy()
migrate = Migrate()

def setup_logging(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=102400, backupCount=20)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Gold Investment startup')

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    with app.app_context():
        db.create_all()

    # Setup logging
    if not app.debug and not app.testing:
        setup_logging(app)
    
    # Register error handlers and authentication
    from app.utils.errors import register_error_handlers
    from app.utils.auth import init_login_manager
    register_error_handlers(app)
    init_login_manager(app)
    
    app.logger.info('Application initialized')

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'ok'})

    # Registrazione dei blueprints
    from app.routes import auth_bp, gold_bp, affiliate_bp
    from app.api.v1.transformations import bp as transformations_bp
    from app.api.v1.transfers import bp as transfers_bp
    from app.api.v1.bonuses import bp as bonuses_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(gold_bp, url_prefix='/api/gold')
    app.register_blueprint(affiliate_bp, url_prefix='/api/affiliate')
    app.register_blueprint(transformations_bp)
    app.register_blueprint(transfers_bp)
    app.register_blueprint(bonuses_bp)

    return app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    return app
