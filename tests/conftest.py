
import pytest
from app import create_app
from app.config.settings import Config
from app.models.models import db
import os

@pytest.fixture
def app():
    app = create_app(Config())
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
