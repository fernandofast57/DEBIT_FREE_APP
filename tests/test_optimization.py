
import pytest
from app import create_app
from app.database import db
from app.utils.optimization import create_indexes
from sqlalchemy import text

def test_table_creation_and_optimization():
    """Test successful table creation and index optimization"""
    app = create_app()
    
    with app.app_context():
        # Clean up existing tables for clean test
        db.drop_all()
        
        # Create tables
        db.create_all()
        
        # Verify tables exist
        result = db.session.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ))
        tables = [row[0] for row in result]
        
        assert 'users' in tables
        assert 'transactions' in tables
        assert 'noble_relations' in tables
        
        # Test index creation
        create_indexes()
        
        # Verify indexes exist
        result = db.session.execute(text(
            "SELECT name FROM sqlite_master WHERE type='index'"
        ))
        indexes = [row[0] for row in result]
        
        assert 'idx_users_email' in indexes
        assert 'idx_transactions_user_id' in indexes
        assert 'idx_noble_relations_user_id' in indexes

