
import os
from typing import List
from flask import Flask
from dotenv import load_dotenv

# Load environment variables from Replit Secrets
load_dotenv()

class Config:
    """Base config using Replit Secrets"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = False
    TESTING = False
    
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
        required = ['SECRET_KEY', 'DATABASE_URL', 'CONTRACT_ADDRESS', 'PRIVATE_KEY', 'RPC_ENDPOINTS']
        missing = [key for key in required if not os.environ.get(key)]
        
        if missing:
            raise ValueError(f"Missing required secrets: {', '.join(missing)}")

        # Validate blockchain addresses
        if not cls.CONTRACT_ADDRESS.startswith('0x') or len(cls.CONTRACT_ADDRESS) != 42:
            raise ValueError('Invalid contract address format')
            
        if not cls.PRIVATE_KEY.startswith('0x') or len(cls.PRIVATE_KEY) != 66:
            raise ValueError('Invalid private key format')

def create_app(config_class=Config):
    """Create Flask app with secure Replit Secrets"""
    app = Flask(__name__)
    
    # Validate secrets before starting
    config_class.validate_config()
    
    app.config.from_object(config_class)
    
    return app
