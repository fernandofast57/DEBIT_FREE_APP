
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
import os

db = SQLAlchemy()
migrate = Migrate()

def setup_logging(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=102400, backupCount=20)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Gold Investment startup')

def create_app(config_class):
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
    app.register_blueprint(auth_bp)
    app.register_blueprint(gold_bp)
    app.register_blueprint(affiliate_bp)

    return app
