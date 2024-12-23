import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, List
from dotenv import load_dotenv
from app.utils.logging_config import APP_NAME

class ConfigValidator:
    """Validatore per la configurazione"""
    REQUIRED_VARS = [
        'SECRET_KEY',
        'DATABASE_URL',
        'CONTRACT_ADDRESS',
        'PRIVATE_KEY',
        'RPC_ENDPOINTS',
        'REDIS_URL' #Added Redis URL to required variables
    ]

    @staticmethod
    def validate() -> bool:
        missing = [var for var in ConfigValidator.REQUIRED_VARS 
                  if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        return True

class LogConfig:
    """Configurazione del sistema di logging"""
    def __init__(self, app_name: str = APP_NAME):
        self.app_name = app_name
        self.log_dir = 'logs'
        self.log_file = f'{self.log_dir}/{app_name}.log'
        self.max_bytes = 10 * 1024 * 1024  # 10MB
        self.backup_count = 5
        self.format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def get_handler(self) -> RotatingFileHandler:
        handler = RotatingFileHandler(
            self.log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        handler.setFormatter(logging.Formatter(self.format))
        return handler

    def setup_logger(self, name: str = None) -> logging.Logger:
        logger = logging.getLogger(name or self.app_name)
        logger.setLevel(logging.INFO)
        logger.addHandler(self.get_handler())
        return logger

class Config:
    """Configurazione base"""
    def __init__(self):
        load_dotenv()
        self.log_config = LogConfig()
        self.logger = self.log_config.setup_logger()
        self.SECRET_KEY = os.getenv('SECRET_KEY')
        self.SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
        self.PRIVATE_KEY = os.getenv('PRIVATE_KEY')
        self.RPC_ENDPOINTS = self._parse_endpoints()
        self.REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0') #Added Redis URL configuration

    def _parse_endpoints(self) -> List[str]:
        endpoints = os.getenv('RPC_ENDPOINTS', '').split(',')
        return [ep.strip() for ep in endpoints if ep.strip()]

    def get_blockchain_config(self) -> Dict[str, Any]:
        return {
            'contract_address': self.CONTRACT_ADDRESS,
            'private_key': self.PRIVATE_KEY,
            'rpc_endpoints': self.RPC_ENDPOINTS
        }

class TestConfig(Config):
    """Test configuration"""
    def __init__(self):
        self.TESTING = True
        self.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        self.WTF_CSRF_ENABLED = False
        self.SECRET_KEY = 'test-key'
        self.CONTRACT_ADDRESS = '0x0000000000000000000000000000000000000000'
        self.PRIVATE_KEY = '0x0000000000000000000000000000000000000000000000000000000000000000'
        self.RPC_ENDPOINTS = ['http://localhost:8545']
        self.REDIS_URL = 'redis://localhost:6379/0' #Added Redis URL for test config