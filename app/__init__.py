
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os

# Inizializzazione delle estensioni
db = SQLAlchemy()
migrate = Migrate()

# ✅ Setup Logging
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')

    # File handler per il logging su file
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=102400, backupCount=20)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    # Console handler per il logging su console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    console_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(console_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Gold Investment startup')



# ✅ Creazione dell'app Flask
def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class())

    # Inizializzazione delle estensioni
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    from app.config.redis_config import RedisConfig
    app.redis = RedisConfig(app.config.get('REDIS_URL'))

    # Garantisce che la cartella `instance` esista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():
        # Import models in dependency order
        from app.models.models import User, BonusTransaction
        from app.models.models import (
            MoneyAccount,
            GoldAccount,
            NobleRank,
            NobleRelation,
            GoldReward,
            Transaction,
            GoldTransformation,
            GoldBar,
            GoldAllocation
        )

        # Ordine corretto per la creazione delle tabelle
        db.drop_all()
        db.create_all()
        db.session.commit()

    # Gestione degli errori
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)

    # Registrazione dei Blueprint
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

    return app