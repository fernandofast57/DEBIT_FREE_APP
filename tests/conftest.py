
import sys
import os
import pytest
from unittest.mock import Mock
from flask import appcontext_pushed

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from app import create_app, db as _db
from app.models.models import User, BonusTransaction
from app.services.blockchain_service import BlockchainService

@pytest.fixture(scope='session')
def app():
    """Create a Flask application object."""
    from config import TestConfig
    app = create_app(TestConfig())
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-key'
    })
    
    ctx = app.app_context()
    ctx.push()
    
    with app.app_context():
        _db.drop_all()
        _db.create_all()
        _db.session.remove()
    
    yield app
    
    _db.session.remove()
    _db.drop_all()
    ctx.pop()

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def db(app):
    """Database fixture."""
    return _db

@pytest.fixture
async def async_client(app):
    """Create an async test client"""
    return app.test_client()

@pytest.fixture
def mock_blockchain_service():
    """Create a mocked blockchain service."""
    mock_service = Mock(spec=BlockchainService)
    mock_service.w3 = Mock()
    mock_service.contract = Mock()
    mock_service.account = Mock()
    mock_service.is_connected.return_value = True
    mock_service.update_noble_rank.return_value = {'status': 'verified', 'transaction_hash': '0x123', 'block_number': 1}
    return mock_service
