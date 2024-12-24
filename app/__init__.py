
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import jsonify
from flask_login import LoginManager
from flask_cors import CORS
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os
from app.models.models import User, MoneyAccount, GoldAccount, GoldTransformation, NobleRank, BonusTransaction  # Aggiunta dell'importazione

db = SQLAlchemy()
migrate = Migrate()

def setup_logging(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/app.log', maxBytes=102400, backupCount=20)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    console_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(console_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Gold Investment startup')

def create_app(config_class=Config):
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

    from app.admin import admin
    admin.init_app(app)
    CORS(app)

    with app.app_context():
      # Drop all existing tables if necessary
      db.drop_all()

      # Create tables in the correct order
      User.__table__.create(db.engine)
      NobleRank.__table__.create(db.engine)
      GoldBar.__table__.create(db.engine)

      MoneyAccount.__table__.create(db.engine)
      GoldAccount.__table__.create(db.engine)
      BonusTransaction.__table__.create(db.engine)
      Transaction.__table__.create(db.engine)
      GoldReward.__table__.create(db.engine)

      NobleRelation.__table__.create(db.engine)
      GoldTransformation.__table__.create(db.engine)
      GoldAllocation.__table__.create(db.engine)

      db.session.commit()

    if not app.debug and not app.testing:
        setup_logging(app)

    from app.utils.errors import register_error_handlers
    register_error_handlers(app)

    from app.routes import auth_bp, gold_bp, affiliate_bp
    from app.api.v1.transformations import bp as transformations_bp
    from app.api.v1.transfers import bp as transfers_bp
    from app.api.v1.bonuses import bp as bonuses_bp
    from app.api.v1.noble import bp as noble_bp
    from app.api.v1.validation import validation_bp
    from app.api.v1.system import bp as system_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(gold_bp, url_prefix='/api/gold')
    app.register_blueprint(affiliate_bp, url_prefix='/api/affiliate')
    app.register_blueprint(transformations_bp, url_prefix='/api/v1/transformations')
    app.register_blueprint(transfers_bp, url_prefix='/api/v1/transfers')
    app.register_blueprint(bonuses_bp, url_prefix='/api/v1/bonuses')
    app.register_blueprint(noble_bp, url_prefix='/api/v1/noble')
    app.register_blueprint(validation_bp, url_prefix='/api/v1/validation')
    app.register_blueprint(system_bp, url_prefix='/api/v1/system')

    from app.utils.optimization import setup_optimization
    app = setup_optimization(app)

    return app