
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base config class"""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RATE_LIMIT = "200/hour"

    # Blockchain config
    CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS')
    SYSTEM_ADDRESS = os.environ.get('SYSTEM_ADDRESS')
    PRIVATE_KEY = os.environ.get('PRIVATE_KEY')

    # RPC endpoints
    RPC_ENDPOINTS = os.environ.get('RPC_ENDPOINTS', '').split(',')
