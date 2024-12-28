
import pytest
from sqlalchemy import inspect, text
from app import create_app
from app.database import db
from app.utils.optimization import create_indexes

def test_table_creation_and_optimization():
    """Test successful table creation and index optimization"""
    app = create_app()
    
    with app.app_context():
        # Clean up existing tables
        db.drop_all()
        
        # Create tables
        db.create_all()
        
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
