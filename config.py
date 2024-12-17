# config.py
import os
from datetime import timedelta

class Config:
    # Base Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///gold_investment.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = int(os.environ.get('DB_POOL_SIZE', 10))
    SQLALCHEMY_MAX_OVERFLOW = int(os.environ.get('DB_MAX_OVERFLOW', 20))
    SQLALCHEMY_POOL_TIMEOUT = int(os.environ.get('DB_POOL_TIMEOUT', 30))

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # Blockchain Configuration
    POLYGON_RPC_URL = os.environ.get('POLYGON_RPC_URL') or 'https://rpc-mumbai.maticvigil.com'
    POLYGON_CHAIN_ID = 80001  # Mumbai testnet
    POLYGON_PRIVATE_KEY = os.environ.get('POLYGON_PRIVATE_KEY')
    SMART_CONTRACT_ADDRESS = os.environ.get('SMART_CONTRACT_ADDRESS')
    MAX_GAS_PRICE_GWEI = 50

    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = 'logs/app.log'

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False