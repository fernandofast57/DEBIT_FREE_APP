from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})

login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    cache.init_app(app)

    db.init_app(app)
    from app.utils.optimization import optimize_queries, create_indexes
    with app.app_context():
        optimize_queries()
        create_indexes()
    migrate.init_app(app, db)
    login_manager.init_app(app)
    admin.init_app(app)

    from app.routes import auth_bp, main_bp
    from app.admin.views import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    return app