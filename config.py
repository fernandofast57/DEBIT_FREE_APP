import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, List
from dotenv import load_dotenv

class ConfigValidator:
    """Validatore per la configurazione"""
    REQUIRED_VARS = [
        'SECRET_KEY',
        'DATABASE_URL',
        'CONTRACT_ADDRESS',
        'PRIVATE_KEY',
        'RPC_ENDPOINTS'
    ]

    @staticmethod
    def validate() -> bool:
        missing = [var for var in ConfigValidator.REQUIRED_VARS 
                  if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        # Validate contract address format
        contract_address = os.getenv('CONTRACT_ADDRESS')
        if not contract_address.startswith('0x') or len(contract_address) != 42:
            raise ValueError("Invalid CONTRACT_ADDRESS format")
        
        # Validate private key format
        private_key = os.getenv('PRIVATE_KEY')
        if not private_key.startswith('0x') or len(private_key) != 66:
            raise ValueError("Invalid PRIVATE_KEY format")
        
        # Validate RPC endpoints
        rpc_endpoints = os.getenv('RPC_ENDPOINTS', '').split(',')
        if not any(ep.strip().startswith('https://') for ep in rpc_endpoints):
            raise ValueError("At least one valid HTTPS RPC endpoint required")
        
        # Validate database URL
        db_url = os.getenv('DATABASE_URL')
        if not any(db_url.startswith(prefix) for prefix in ['sqlite:///', 'postgresql://', 'mysql://']):
            raise ValueError("Invalid DATABASE_URL format")
            
        return True

class LogConfig:
    """Configurazione del sistema di logging"""
    def __init__(self, app_name: str = 'gold-investment'):
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
        # Carica variabili d'ambiente
        load_dotenv()
        
        # Valida configurazione
        ConfigValidator.validate()
        
        # Setup logging
        self.log_config = LogConfig()
        self.logger = self.log_config.setup_logger()
        
        # Configurazione base
        self.SECRET_KEY = os.getenv('SECRET_KEY')
        db_path = os.path.join('instance', 'gold_investment.db')
        self.SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', f'sqlite:///{db_path}')
        os.makedirs('instance', exist_ok=True)
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
        self.PRIVATE_KEY = os.getenv('PRIVATE_KEY')
        self.RPC_ENDPOINTS = self._parse_endpoints()
        
        self.logger.info("Configuration loaded successfully")

    def _parse_endpoints(self) -> List[str]:
        """Parse RPC endpoints from environment"""
        endpoints = os.getenv('RPC_ENDPOINTS', '').split(',')
        return [ep.strip() for ep in endpoints if ep.strip()]

    def get_blockchain_config(self) -> Dict[str, Any]:
        """Get blockchain specific configuration"""
        return {
            'contract_address': self.CONTRACT_ADDRESS,
            'private_key': self.PRIVATE_KEY,
            'rpc_endpoints': self.RPC_ENDPOINTS
        }