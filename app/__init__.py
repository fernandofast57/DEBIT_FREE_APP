from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, jsonify
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
    # File handler
    app.logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    console_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(console_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('Gold Investment startup')

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class())
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
        
    db.init_app(app)
    migrate.init_app(app, db)
    
    from app.admin import admin
    admin.init_app(app)
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
    from app.api.v1.noble import noble_bp
    from app.api.v1.validation import validation_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(gold_bp, url_prefix='/api/gold')
    app.register_blueprint(affiliate_bp, url_prefix='/api/affiliate')
    app.register_blueprint(transformations_bp)
    app.register_blueprint(transfers_bp)
    app.register_blueprint(bonuses_bp)
    app.register_blueprint(noble_bp, url_prefix='/api/v1/noble')
    app.register_blueprint(validation_bp, url_prefix='/api/v1/system')

    return app