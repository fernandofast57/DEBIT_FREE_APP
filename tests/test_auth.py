
import pytest
from app import create_app
from app.models.models import User, db
from app.utils.auth import AuthManager
from unittest.mock import Mock

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_manager():
    return AuthManager('test_secret_key')

def test_token_generation(auth_manager):
    token = auth_manager.generate_token(1, 'test_device')
    assert token is not None
    
def test_token_verification(auth_manager):
    token = auth_manager.generate_token(1, 'test_device')
    payload = auth_manager.verify_token(token)
    assert payload is not None
    assert payload['user_id'] == 1
    assert payload['device_id'] == 'test_device'

def test_invalid_token(auth_manager):
    payload = auth_manager.verify_token('invalid_token')
    assert payload is None
