
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

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig())
    return app

@pytest.fixture(scope='session')
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()

@pytest.fixture(scope='function')
def session(db):
    connection = db.engine.connect()
    transaction = connection.begin()
    session = db.create_scoped_session()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
