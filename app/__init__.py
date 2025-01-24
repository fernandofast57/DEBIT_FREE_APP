from flask import Flask
from flask_caching import Cache
from flask_migrate import Migrate
from flask_login import LoginManager
from app.middleware.security import SecurityMiddleware
from app.utils.load_balancer import load_balancer
from app.utils.robust_rate_limiter import RobustRateLimiter
from app.utils.monitoring import setup_monitoring
from app.models import db
import logging
from logging.handlers import RotatingFileHandler
import os

# Initialize extensions
cache = Cache()
login_manager = LoginManager()
migrate = Migrate()
security_middleware = SecurityMiddleware()
rate_limiter = RobustRateLimiter()

def setup_logging(app, config_name):
    if not os.path.exists('logs'):
        os.mkdir('logs')

    log_level = logging.DEBUG if config_name == 'development' else logging.INFO
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )

    handlers = {
        'app': RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10),
        'error': RotatingFileHandler('logs/error.log', maxBytes=10240, backupCount=10),
        'security': RotatingFileHandler('logs/security.log', maxBytes=10240, backupCount=10)
    }

    for handler in handlers.values():
        handler.setFormatter(formatter)
        handler.setLevel(log_level)
        app.logger.addHandler(handler)

    app.logger.setLevel(log_level)
    app.logger.info(f'Gold Investment App startup in {config_name} mode')

def create_app(config_name='production'):
    app = Flask(__name__, instance_relative_config=True)

    # Import config after initializing app
    from app.config.settings import ProductionConfig, DevelopmentConfig, TestingConfig
    config_classes = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    app.config.from_object(config_classes.get(config_name, ProductionConfig))

    setup_logging(app, config_name)

    # Initialize extensions with app context
    db.init_app(app)
    cache.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Setup login manager
    from app.models.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please log in to access this page."

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.transformations import transform_bp
    from app.api.v1.transformations import transformations_bp
    from app.api.v1.accounting import bp as accounting_bp
    from app.api.v1.system import bp as system_bp
    from app.admin.views import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(transformations_bp, url_prefix='/api/v1/transformations')
    app.register_blueprint(accounting_bp, url_prefix='/api/v1/accounts')
    app.register_blueprint(system_bp, url_prefix='/api/v1')

    # Setup production services
    if config_name == 'production':
        load_balancer.register_server('0.0.0.0', 8080)
        load_balancer.register_server('0.0.0.0', 8081)
        setup_monitoring(app)

    # Initialize database
    if not os.path.exists(app.config['SQLALCHEMY_DATABASE_URI']):
        with app.app_context():
            db.create_all()
            app.logger.info("Database initialized successfully")

    #Added dependency check
    from app.utils.monitoring.dependency_monitor import check_dependencies
    check_dependencies(app)

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