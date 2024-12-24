
import pytest
from app import create_app, db as _db
import asyncio

@pytest.fixture(scope='session')
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope='session')
async def app():
    """Create a Flask application object."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False
    })
    
    async with app.app_context():
        # Ensure all models are imported
        from app.models.models import User, BonusTransaction, NobleRelation, GoldAccount, MoneyAccount
        # Ricrea le tabelle in ordine corretto
        await _db.drop_all()
        await _db.create_all()
        yield app
        await _db.drop_all()

@pytest.fixture
async def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture(scope='session')
def db(app):
    """Create a database object."""
    return _db
