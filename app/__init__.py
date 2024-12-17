
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    from app.api.v1 import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    from app.routes import auth_bp, gold_bp, affiliate_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(gold_bp)
    app.register_blueprint(affiliate_bp)
    
    return app
