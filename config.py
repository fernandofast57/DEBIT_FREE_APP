
import os
from typing import Optional, List
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///instance/gold_investment.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Blockchain configuration
    CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
    BLOCKCHAIN_PRIVATE_KEY = os.getenv('PRIVATE_KEY')
    RPC_ENDPOINTS = os.getenv('RPC_ENDPOINTS', '').split(',')
