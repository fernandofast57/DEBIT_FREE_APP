from flask import Flask
from flask_login import LoginManager
from config import Config
from app.models import db
from app.admin import admin

login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    admin.init_app(app)

    from app.routes import auth_bp, main_bp
    from app.admin.views import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    return app