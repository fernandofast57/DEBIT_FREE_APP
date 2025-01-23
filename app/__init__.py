
# app/__init__.py
from flask import Flask
from app.routes.transformations import transform_bp
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_login import LoginManager
from flask_migrate import Migrate
from app.config.settings import Config, ProductionConfig, DevelopmentConfig, TestingConfig
from app.models import db
from app.admin import admin
from app.models.models import User
from sqlalchemy import text, inspect
import logging
from logging.handlers import RotatingFileHandler
import os
from app.middleware.security import SecurityMiddleware
from app.utils.load_balancer import load_balancer
from app.utils.rate_limiter import RateLimiter
from app.utils.monitoring import setup_monitoring

# Inizializzazione estensioni Flask
cache = Cache()
login_manager = LoginManager()
migrate = Migrate()
security_middleware = SecurityMiddleware()
rate_limiter = RateLimiter()

def setup_logging(app, config_name):
    """Configura il logging in base all'ambiente"""
    if not os.path.exists('logs'):
        os.mkdir('logs')
        
    log_level = logging.DEBUG if config_name == 'development' else logging.INFO
    
    handlers = {
        'app': RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10),
        'error': RotatingFileHandler('logs/error.log', maxBytes=10240, backupCount=10),
        'security': RotatingFileHandler('logs/security.log', maxBytes=10240, backupCount=10)
    }
    
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    for handler in handlers.values():
        handler.setFormatter(formatter)
        handler.setLevel(log_level)
        app.logger.addHandler(handler)
    
    app.logger.setLevel(log_level)
    app.logger.info(f'Gold Investment App startup in {config_name} mode')

def register_extensions(app):
    """Registra le estensioni Flask"""
    cache.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app)

def register_blueprints(app):
    """Registra i blueprint dell'applicazione"""
    from app.routes import auth_bp, main_bp
    from app.admin.views import admin_bp
    from app.api.v1.transformations import transformations_bp
    from app.api.v1.accounting import bp as accounting_bp
    from app.api.v1.system import bp as system_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(transformations_bp, url_prefix='/api/v1/transformations')
    app.register_blueprint(accounting_bp, url_prefix='/api/v1/accounts')
    app.register_blueprint(system_bp, url_prefix='/api/v1')

def configure_security(app):
    """Configura le misure di sicurezza"""
    @app.before_request
    def before_request():
        return security_middleware.check_request()

    @app.after_request
    def after_request(response):
        return security_middleware.process_response(response)

def init_db(app):
    """Inizializza il database e crea le tabelle se necessario"""
    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table('users'):
            db.create_all()
            app.logger.info("Database tables created successfully")

def create_app(config_name='production'):
    """Factory pattern per la creazione dell'app Flask"""
    app = Flask(__name__, instance_relative_config=True)
    
    # Configurazione basata sull'ambiente
    config_classes = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    app.config.from_object(config_classes.get(config_name, ProductionConfig))

    # Setup del logging
    setup_logging(app, config_name)
    
    # Registrazione estensioni
    register_extensions(app)
    
    # Configurazione login manager
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message = "Please log in to access this page."

    # Setup load balancer per produzione
    if config_name == 'production':
        load_balancer.register_server('0.0.0.0', 8080)
        load_balancer.register_server('0.0.0.0', 8081)
        setup_monitoring(app)

    # Inizializzazione database
    init_db(app)
    
    # Registrazione blueprints
    register_blueprints(app)
    
    # Configurazione sicurezza
    configure_security(app)
    
    app.logger.info('Application startup complete')
    
    return app

# Configurazione per l'esecuzione diretta
if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False,
        use_reloader=False,
        threaded=True
    )
