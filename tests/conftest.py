import sys
import os
import pytest
import asyncio

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from app import create_app, db as _db
from app.models.models import User, BonusTransaction

@pytest.fixture(scope='session')
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope='session')
async def app():
    """Create a Flask application object."""
    from config import TestConfig
    app = create_app(TestConfig)
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False
    })
    
    async with app.app_context():
        # Clean state
        _db.drop_all()
        # Create tables in correct order
        _db.create_all()
        # Ensure session is clean
        _db.session.remove()
        yield app
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
async def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def db(app):
    """Database fixture."""
    return _db