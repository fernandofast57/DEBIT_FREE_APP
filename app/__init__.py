
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

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    console_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(console_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Gold Investment startup')

def create_app(config_class):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class())

    from app.config.redis_config import RedisConfig
    app.redis = RedisConfig(app.config.get('REDIS_URL'))

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    with app.app_context():
        from app.models.models import User, MoneyAccount, GoldAccount, GoldTransformation, NobleRank, BonusTransaction

        # Drop all existing tables if necessary
        db.drop_all()

        # Create tables in the correct order
        User.__table__.create(db.engine)
        NobleRank.__table__.create(db.engine)
        # Includi qui le altre tabelle se necessario...

        db.session.commit()

    setup_logging(app)

    from app.utils.errors import register_error_handlers
    register_error_handlers(app)

    from app.routes import auth_bp, gold_bp, affiliate_bp
    # registra i blueprint come hai già fatto

    return app