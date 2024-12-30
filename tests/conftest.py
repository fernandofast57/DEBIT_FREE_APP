
import pytest
import asyncio
from functools import wraps
from app import create_app
from app.database import db as _db
from config import TestConfig

def async_test(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        async def wrapped():
            return await f(*args, **kwargs)
        return asyncio.run(wrapped())
    return wrapper

@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig())
    return app

@pytest.fixture(scope='session')
def db(app):
    """Session-wide test database"""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()

@pytest.fixture(scope='function')
def session(db):
    """Creates a new database session for each test"""
    connection = db.engine.connect()
    transaction = connection.begin()
    session = db.create_scoped_session()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope='function')
def client(app):
    """Test client for the Flask application"""
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    """Test CLI runner for the Flask application"""
    return app.test_cli_runner()
