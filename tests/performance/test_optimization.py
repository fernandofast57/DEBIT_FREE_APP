
import pytest
from sqlalchemy import inspect, text
from app.database import db
from app.utils.optimization import create_indexes, optimize_queries
from app.models.models import User, NobleRank, Transaction
import time

@pytest.fixture
def test_db(app):
    """Setup test database"""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

async def test_index_creation(test_db):
    """Test creation of database indexes"""
    await create_indexes()
    inspector = inspect(db.engine)
    
    # Verify indexes on key tables
    transaction_indexes = inspector.get_indexes('transactions')
    assert any(idx['name'] == 'idx_transactions_user' for idx in transaction_indexes)
    assert any(idx['name'] == 'idx_transactions_status' for idx in transaction_indexes)

async def test_query_optimization(test_db):
    """Test query performance optimizations"""
    await optimize_queries()
    
    with db.engine.connect() as conn:
        # Verify PRAGMA settings
        pragmas = {
            'journal_mode': 'WAL',
            'synchronous': 'NORMAL',
            'cache_size': 10000,
            'temp_store': 'MEMORY'
        }
        
        for pragma, expected_value in pragmas.items():
            result = conn.execute(text(f"PRAGMA {pragma}")).scalar()
            assert str(result).upper() == str(expected_value).upper()

async def test_query_performance(test_db):
    """Test actual query performance improvements"""
    # Insert test data
    users = []
    for i in range(100):
        user = User(username=f"test_user_{i}", 
                   email=f"test{i}@example.com")
        users.append(user)
    
    db.session.add_all(users)
    await db.session.commit()
    
    # Measure query performance
    start_time = time.time()
    result = await db.session.execute(
        text("SELECT * FROM users WHERE username LIKE 'test_user_%'")
    )
    query_time = time.time() - start_time
    
    # Verify reasonable performance
    assert query_time < 1.0  # Should complete within 1 second
    assert len(result.all()) == 100

async def test_transaction_performance(test_db):
    """Test transaction processing performance"""
    user = User(username="performance_test", 
                email="perf@example.com")
    db.session.add(user)
    await db.session.commit()
    
    start_time = time.time()
    for i in range(50):
        transaction = Transaction(
            user_id=user.id,
            amount=100,
            type='test'
        )
        db.session.add(transaction)
    
    await db.session.commit()
    total_time = time.time() - start_time
    
    # Verify batch insert performance
    assert total_time < 2.0  # Should complete within 2 seconds

async def test_concurrent_access(test_db):
    """Test database behavior under concurrent access"""
    async def add_user(username):
        user = User(username=username, 
                   email=f"{username}@example.com")
        db.session.add(user)
        await db.session.commit()
        return user.id
    
    # Execute concurrent operations
    import asyncio
    tasks = [add_user(f"concurrent_user_{i}") for i in range(10)]
    user_ids = await asyncio.gather(*tasks)
    
    # Verify all users were created
    assert len(user_ids) == 10
    assert len(set(user_ids)) == 10  # All IDs should be unique
