
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flasgger import Swagger
import logging
from logging.handlers import RotatingFileHandler
import os

db = SQLAlchemy()
migrate = Migrate()
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}
swagger = Swagger(template={
    "swagger": "2.0",
    "info": {
        "title": "Gold Investment API",
        "description": "API for Gold Investment Platform",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header"
        }
    }
})

def setup_logging(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')
        
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        '\nPath: %(pathname)s:%(lineno)d'
        '\nRequest ID: %(request_id)s'
    )
    
    # Main application log
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=1024000, backupCount=20)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Error log
    error_handler = RotatingFileHandler('logs/error.log', maxBytes=1024000, backupCount=10)
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Gold Investment startup')

def create_app(config_class):
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    
    if os.getenv('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=os.getenv('SENTRY_DSN'),
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0,
            environment='production' if not os.getenv('FLASK_DEBUG') else 'development'
        )
    
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class())
    
    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app)

    with app.app_context():
        from app.models.models import (User, MoneyAccount, GoldAccount, 
                                     GoldTransformation, NobleRank, NobleRelation,
                                     Transaction, GoldBar, GoldAllocation,
                                     GoldReward, BonusTransaction)
        db.create_all()

    setup_logging(app)

    from app.routes import auth_bp, gold_bp, affiliate_bp
    from app.routes.main import bp as main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(gold_bp)
    app.register_blueprint(affiliate_bp)
    app.register_blueprint(main_bp)
    
    swagger.init_app(app)

    return app
