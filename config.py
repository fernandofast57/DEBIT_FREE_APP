class Config:
    """Base config class"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///gold_investment.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RATE_LIMIT = "200/hour"

    # Blockchain config
    CONTRACT_ADDRESS = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
    SYSTEM_ADDRESS = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
    PRIVATE_KEY = 'your-private-key'  # Usa variabili d'ambiente in produzione

    # RPC endpoints
    RPC_ENDPOINTS = [
        "https://rpc-mumbai.maticvigil.com",
        "https://matic-mumbai.chainstacklabs.com",
        "https://matic-testnet-archive-rpc.bwarelabs.com"
    ]

# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    # Registra blueprints
    from app.routes import main
    app.register_blueprint(main.bp)

    return app

# tests/conftest.py
import pytest
from app import create_app, db
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()