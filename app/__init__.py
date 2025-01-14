
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from app.database import db
from app.admin import admin
from app.models.models import User, NobleRank, Transaction
from sqlalchemy import text
from app.utils.database.migrations import MigrationManager

# Inizializzazione estensioni Flask
cache = Cache(config={'CACHE_TYPE': 'simple'})
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    """Factory per creare l'app Flask."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Inizializzazione delle estensioni
    cache.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)  # Manteniamo Flask-Migrate per compatibilità

    # Configurazione del login_manager
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message = "Please log in to access this page."

    # Inizializzazione Load Balancer
    from app.utils.load_balancer import load_balancer
    load_balancer.register_server('0.0.0.0', 8080)
    load_balancer.register_server('0.0.0.0', 8081)

    # Ottimizzazioni Database
    with app.app_context():
        from app.utils.optimization import optimize_queries, create_indexes
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if not inspector.has_table('users'):
            db.create_all()
            print("Tables created successfully.")
            optimize_queries()
            create_indexes()
        else:
            optimize_queries()

    # Inizializzazione Admin
    admin.init_app(app)

    # Inizializzazione Migration Manager con logging avanzato
    migration_manager = MigrationManager(app, db)
    migration_manager.init_migrations()
    migration_manager.apply_migrations()  # Applica automaticamente le migrazioni pendenti

    # Blueprint Registration
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

    return app
