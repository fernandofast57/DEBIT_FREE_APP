import pytest
from sqlalchemy import inspect, text
from app import create_app, db
from app.utils.optimization import create_indexes
from app.models.models import User, NobleRank, Transaction

@pytest.fixture(scope='function')
def test_app():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()  # Create all tables before testing
        yield app
        db.session.remove()
        db.drop_all()

def test_table_creation_and_optimization(test_app):
    """Test successful table creation and index optimization"""
    with test_app.app_context():
        db.create_all()  # Ensure tables are created
        # Get inspector
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        # Verify core tables exist
        assert 'users' in tables, "Users table not found"
        assert 'noble_ranks' in tables, "Noble ranks table not found"
        assert 'transactions' in tables, "Transactions table not found"
        
        # Create indexes
        create_indexes()
        
        # Verify indexes
        indexes = inspector.get_indexes('users')
        index_names = [idx['name'] for idx in indexes]
        assert 'idx_users_email' in index_names, "Email index not created"
        
        # Verify foreign keys
        fks = inspector.get_foreign_keys('noble_ranks')
        assert any(fk['referred_table'] == 'users' for fk in fks), "User foreign key not found"