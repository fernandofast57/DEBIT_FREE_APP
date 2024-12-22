
import pytest
import asyncio
from app import create_app
from app.models.models import db as _db

@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope='session')
async def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    async with app.app_context():
        await _db.create_all()
        yield app
        await _db.drop_all()

@pytest.fixture
async def client(app):
    return app.test_client()

@pytest.fixture(scope='session')
async def db(app):
    return _db
