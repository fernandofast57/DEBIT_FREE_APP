
import pytest
from app import create_app
from app.database import db as _db
from config import TestConfig

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
