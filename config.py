import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    TESTING = False

    # Cache configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300

    # Security settings
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    REMEMBER_COOKIE_DURATION = timedelta(days=7)


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

    # Override with strong secret key in production
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Security settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

    # SSL/TLS settings
    SSL_REDIRECT = True

    # Cache configuration
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')

    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL')

    # Logging
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT',
                                   'false').lower() in ['true', 't', '1']


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True
    JWT_SECRET_KEY = 'dev-secret-key'
    BLOCKCHAIN_RPC_URL = 'http://127.0.0.1:8545'