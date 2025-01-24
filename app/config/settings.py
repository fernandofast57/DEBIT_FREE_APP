
import os
from datetime import timedelta

class Config:
    HOST = "0.0.0.0"
    PORT = int(os.getenv('PORT', 8080))
    
    # Redis Configuration
    REDIS_HOST = "0.0.0.0"
    REDIS_PORT = 6379
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    
    # Cache Configuration
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_REDIS_URL = REDIS_URL
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///instance/gold_investment.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    PASSWORD_SALT = os.getenv('PASSWORD_SALT', 'dev-salt')
    
    # JWT Configuration
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Rate Limiting
    RATE_LIMIT_DEFAULT = "50 per minute"
    
    # Async Configuration
    ASYNC_MODE = True
    ASYNC_WORKERS = 4
    
class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
