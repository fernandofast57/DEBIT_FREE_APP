
from flask import Flask
from config import Config
from app.database import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from app.api.v1.transformations import transformations_bp
    from app.routes.main import bp as main_bp
    
    app.register_blueprint(transformations_bp, url_prefix='/api/v1/transformations')
    app.register_blueprint(main_bp)
    
    return app
