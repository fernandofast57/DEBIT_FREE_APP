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
from app.utils.database.migrations import migration_manager # Added this line

cache = Cache(config={'CACHE_TYPE': 'simple'})
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    cache.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    migration_manager.init_app(app, db) # Added this line

    with app.app_context():
        if not app.config.get('TESTING'):
            from app.utils.optimization import optimize_queries, create_indexes
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            if not inspector.has_table('users'):  # Check if tables exist
                db.create_all()
                print("Tables created successfully.")
                optimize_queries()
                create_indexes()
            else:
                optimize_queries()  # Still run optimizations for existing tables

    login_manager.init_app(app)
    admin.init_app(app)

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