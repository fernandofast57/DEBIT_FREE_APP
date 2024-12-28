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

cache = Cache(config={'CACHE_TYPE': 'simple'})
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    cache.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        # Create tables first
        db.create_all()
        print("Tables created successfully.")

        # Run optimizations and create indexes after tables
        from app.utils.optimization import optimize_queries, create_indexes
        optimize_queries()
        create_indexes()

    login_manager.init_app(app)
    admin.init_app(app)

    from app.routes import auth_bp, main_bp
    from app.admin.views import admin_bp
    from app.api.v1.transformations import transformations_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(transformations_bp, url_prefix='/api/v1/transformations')

    return app