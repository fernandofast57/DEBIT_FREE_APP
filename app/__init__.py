# app/__init__.py
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()

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
    from app.utils.logging_config import setup_logging
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