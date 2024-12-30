import pytest
from decimal import Decimal
from app import create_app, db
from app.models.models import User, MoneyAccount, GoldAccount
from flask_migrate import upgrade, downgrade

@pytest.fixture(scope='session')
def app():
    """Create a Flask application object for testing."""
    from config import TestConfig
    
    app = create_app(TestConfig())
    
    with app.app_context():
        # Reset database state
        downgrade(revision='base')
        upgrade()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(autouse=True)
def cleanup_after_test(app):
    """Clean up after each test."""
    yield
    with app.app_context():
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

@pytest.fixture(autouse=True)
def db_session(app):
    """Create a new database session for each test."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        options = dict(bind=connection, binds={})
        session = db.create_scoped_session(options=options)
        
        db.session = session
        
        yield session
        
        transaction.rollback()
        connection.close()
        session.remove()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create a test user with associated accounts."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        user.money_account = MoneyAccount(balance=Decimal('2000.00'))
        user.gold_account = GoldAccount(balance=Decimal('0.00'))
        db.session.add(user)
        db.session.commit()
        
        yield user
        
        # Cleanup after test
        db.session.delete(user)
        db.session.commit()

@pytest.fixture
def auth_headers(test_user):
    """Generate authentication headers for test user."""
    return {'Authorization': f'Bearer test_token_{test_user.id}'}