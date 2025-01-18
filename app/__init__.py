# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_login import LoginManager
from flask_migrate import Migrate
from app.config.settings import Config, ProductionConfig
from app.database import db
from app.admin import admin
from app.models.models import User, NobleRank, Transaction
from sqlalchemy import text, inspect
import logging
from logging.handlers import RotatingFileHandler
import os

# Inizializzazione estensioni Flask
cache = Cache(config={'CACHE_TYPE': 'simple'})
login_manager = LoginManager()
migrate = Migrate()


# Configurazione logging per produzione
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


def create_app(config_class=ProductionConfig):
    """Factory per creare l'app Flask."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Inizializzazione delle estensioni
    cache.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Setup logging per produzione
    if not app.debug and not app.testing:
        setup_logging(app)

    # Configurazione del login_manager
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message = "Please log in to access this page."

    # Inizializzazione Load Balancer per produzione
    from app.utils.load_balancer import load_balancer
    load_balancer.register_server('0.0.0.0', 8080)
    load_balancer.register_server('0.0.0.0', 8081)

    # Ottimizzazioni Database
    with app.app_context():
        from app.utils.optimization import optimize_queries, create_indexes
        inspector = inspect(db.engine)

        if not inspector.has_table('users'):
            db.create_all()
            app.logger.info("Tables created successfully.")
            optimize_queries()
            create_indexes()
        else:
            optimize_queries()

    # Inizializzazione Admin
    admin.init_app(app)

    # Registrazione Blueprint
    from app.routes import auth_bp, main_bp
    from app.admin.views import admin_bp
    from app.api.v1.transformations import transformations_bp
    from app.api.v1.accounting import bp as accounting_bp
    from app.api.v1.system import bp as system_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(transformations_bp,
                           url_prefix='/api/v1/transformations')
    app.register_blueprint(accounting_bp, url_prefix='/api/v1/accounts')
    app.register_blueprint(system_bp, url_prefix='/api/v1')

    # Log dell'avvio completato
    app.logger.info('Application startup complete')

    return app


# Configurazione per l'esecuzione diretta
if __name__ == '__main__':
    app = create_app(ProductionConfig)
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False,
        use_reloader=False,  # Disabilita il reloader in produzione
        threaded=True  # Abilita il multi-threading
    )
