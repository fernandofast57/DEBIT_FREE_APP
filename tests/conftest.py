
import pytest
from decimal import Decimal
from app import create_app, db as _db
from app.models.models import User, MoneyAccount, GoldAccount

@pytest.fixture(scope='session')
def app():
    """Create a Flask application object for testing."""
    from config import TestConfig
    app = create_app(TestConfig())
    
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def db(app):
    """Database fixture."""
    return _db

@pytest.fixture
def test_user(app, db):
    """Create a test user with associated accounts."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        user.money_account = MoneyAccount(balance=Decimal('2000.00'))
        user.gold_account = GoldAccount(balance=Decimal('0.00'))
        db.session.add(user)
        db.session.commit()
        return user
