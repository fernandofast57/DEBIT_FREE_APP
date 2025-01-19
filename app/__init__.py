# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_login import LoginManager
from flask_migrate import Migrate
from app.config import Config
from app.database import db, migrate
from app.admin import admin
from app.models.models import User, NobleRank, Transaction
from sqlalchemy import text, inspect
import logging
from logging.handlers import RotatingFileHandler
import os

# Initialize Flask extensions
cache = Cache(config={'CACHE_TYPE': 'simple'})
login_manager = LoginManager()

def setup_logging(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/gold_app.log',
                                     maxBytes=10240,
                                     backupCount=10)
    file_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Gold Investment App startup')

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_object(Config)
    else:
        app.config.from_object(test_config)

    # Initialize extensions
    cache.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app)

    # Setup logging for production
    if not app.debug and not app.testing:
        setup_logging(app)

    # Configure login manager
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message = "Please log in to access this page."


    # Register blueprints
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

    # Log the completed startup
    app.logger.info('Application startup complete')

    return app


# Configuration for direct execution
if __name__ == '__main__':
    app = create_app(Config)
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False,
        use_reloader=False,  # Disable the reloader in production
        threaded=True  # Enable multi-threading
    )