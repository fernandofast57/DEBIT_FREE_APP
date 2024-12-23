
import pytest
from app import create_app
from app.models import User, NobleRank, NobleRelation, db
from app.utils.auth import AuthManager
from decimal import Decimal

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

def test_noble_relation_verification(app, auth_manager):
    with app.app_context():
        db.create_all()
        
        noble_rank = NobleRank(rank_name='Silver', min_investment=Decimal('5000.00'))
        db.session.add(noble_rank)
        db.session.commit()
        
        user = User(email='noble@test.com', noble_rank_id=noble_rank.id)
        db.session.add(user)
        db.session.commit()
        
        noble_relation = NobleRelation(
            user_id=user.id,
            noble_rank_id=noble_rank.id,
            verification_status='to_be_verified'
        )
        db.session.add(noble_relation)
        db.session.commit()

        token = auth_manager.generate_token(user.id, 'test_device')
        payload = auth_manager.verify_token(token)
        
        assert payload is not None
        assert payload['user_id'] == user.id
        assert noble_relation.verification_status == 'to_be_verified'
        
        db.session.remove()
        db.drop_all()

def test_token_verification(app, auth_manager):
    with app.app_context():
        token = auth_manager.generate_token(1, 'test_device')
        payload = auth_manager.verify_token(token)
        assert payload is not None
        assert payload['user_id'] == 1
        assert payload['device_id'] == 'test_device'

def test_invalid_token(app, auth_manager):
    with app.app_context():
        invalid_token = "invalid.token.string"
        payload = auth_manager.verify_token(invalid_token)
        assert payload is None
