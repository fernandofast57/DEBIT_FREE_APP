
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from app.utils.security import SecurityManager
import logging
from logging.handlers import RotatingFileHandler
import os

db = SQLAlchemy()
migrate = Migrate()

def setup_logging(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=102400, backupCount=20)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Gold Investment startup')

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class())

    # Initialize security manager
    security_manager = SecurityManager(
        app_name='gold-investment',
        redis_url='redis://0.0.0.0:6379/0'
    )
    app.rate_limiter = security_manager.rate_limiter
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    with app.app_context():
        db.create_all()

    # Setup logging
    if not app.debug and not app.testing:
        setup_logging(app)

    # Register error handlers
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)

    # Register blueprints
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
