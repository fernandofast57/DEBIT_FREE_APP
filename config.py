
import os
from typing import List
from flask import Flask
from dotenv import load_dotenv

# Load environment variables from Replit Secrets
load_dotenv()

class Config:
    """Base config using Replit Secrets"""
    
    # Required secrets
    REQUIRED_SECRETS = {
        'SECRET_KEY': 'Flask secret key for session security',
        'DATABASE_URL': 'Database connection URL',
        'CONTRACT_ADDRESS': 'Blockchain contract address',
        'PRIVATE_KEY': 'Private key for blockchain transactions',
        'RPC_ENDPOINTS': 'Comma-separated RPC endpoints'
    }
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    TESTING = os.environ.get('TESTING', 'False').lower() == 'true'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Blockchain settings
    CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS')
    PRIVATE_KEY = os.environ.get('PRIVATE_KEY')
    RPC_ENDPOINTS = os.environ.get('RPC_ENDPOINTS', '').split(',')
    
    # Noble ranks thresholds
    NOBLE_THRESHOLD = 10000
    VISCOUNT_THRESHOLD = 50000
    COUNT_THRESHOLD = 100000

    @classmethod
    def validate_config(cls):
        """Validate required secrets are present"""
        missing = []
        invalid = []
        
        for key, description in cls.REQUIRED_SECRETS.items():
            value = os.environ.get(key)
            if not value:
                missing.append(f"{key} ({description})")
            elif key == 'CONTRACT_ADDRESS' and (not value.startswith('0x') or len(value) != 42):
                invalid.append(f"{key}: Invalid contract address format")
            elif key == 'PRIVATE_KEY' and (not value.startswith('0x') or len(value) != 66):
                invalid.append(f"{key}: Invalid private key format")
        
        if missing:
            raise ValueError(f"Missing required secrets: {', '.join(missing)}")
        if invalid:
            raise ValueError(f"Invalid secret values: {', '.join(invalid)}")

def create_app(config_class=Config):
    """Create Flask app with secure Replit Secrets"""
    app = Flask(__name__)
    
    # Validate secrets before starting
    config_class.validate_config()
    
    app.config.from_object(config_class)
    return app
