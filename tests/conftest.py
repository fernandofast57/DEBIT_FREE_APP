
import pytest
import asyncio
from functools import wraps
from app import create_app
from app.database import db as _db
from app.config.constants import TestConfig
from app.models.models import User, MoneyAccount, GoldAccount
from decimal import Decimal

def async_test(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        async def wrapped():
            return await f(*args, **kwargs)
        return asyncio.run(wrapped())
    return wrapper

@pytest.fixture(scope='session')
def app():
    """Create and configure a test application instance"""
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

@pytest.fixture(scope='function')
def test_user(session):
    """Create a test user with associated accounts"""
    user = User(
        email="test@example.com",
        username="test_user",
        blockchain_address="0x123test456"
    )
    money_account = MoneyAccount(balance=Decimal('1000.00'))
    gold_account = GoldAccount(balance=Decimal('0'))
    
    user.money_account = money_account
    user.gold_account = gold_account
    
    session.add(user)
    session.commit()
    
    yield user
    
    session.delete(user)
    session.commit()
