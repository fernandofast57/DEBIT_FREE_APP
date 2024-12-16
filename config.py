
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', "dev-secret-key")
    
    # Blockchain configuration
    WEB3_PROVIDER = os.getenv('WEB3_PROVIDER', "http://0.0.0.0:8545")
    CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = 'logs/app.log'
    LOG_MAX_BYTES = 1024 * 1024  # 1MB
    LOG_BACKUP_COUNT = 10

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    WEB3_PROVIDER = "http://0.0.0.0:8545"
