import pytest
from sqlalchemy import inspect, text
from app.database import db
from app.utils.optimization import create_indexes, optimize_queries
import asyncio

@pytest.mark.asyncio
async def test_index_creation(app):
    """Test creation of database indexes"""
    async with app.app_context():
        await create_indexes()
        inspector = inspect(db.engine)

        # Verify indexes on key tables
        transaction_indexes = inspector.get_indexes('transactions')
        assert any(idx['name'] == 'idx_transactions_user' for idx in transaction_indexes)
        assert any(idx['name'] == 'idx_transactions_status' for idx in transaction_indexes)

@pytest.mark.asyncio
async def test_query_optimization(app):
    """Test query performance optimizations"""
    async with app.app_context():
        await optimize_queries()

        async with db.engine.connect() as conn:
            # Verify PRAGMA settings
            pragmas = {
                'journal_mode': 'WAL',
                'synchronous': 'NORMAL',
                'cache_size': 10000,
                'temp_store': 'MEMORY'
            }

            for pragma, expected_value in pragmas.items():
                result = await conn.execute(text(f"PRAGMA {pragma}"))
                value = await result.scalar()
                assert str(value).upper() == str(expected_value).upper()

@pytest.mark.asyncio
async def test_query_performance(app):
    async with app.app_context():
        start_time = asyncio.get_event_loop().time()
        async with db.engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        duration = asyncio.get_event_loop().time() - start_time
        assert duration < 1.0  # Should complete within 1 second

@pytest.mark.asyncio
async def test_transaction_performance(app):
    async with app.app_context():
        start_time = asyncio.get_event_loop().time()
        async with db.engine.begin() as conn:
            await conn.execute(text("BEGIN TRANSACTION"))
            await conn.execute(text("COMMIT"))
        duration = asyncio.get_event_loop().time() - start_time
        assert duration < 1.0

@pytest.mark.asyncio
async def test_concurrent_access(app):
    async with app.app_context():
        async def access_db():
            async with db.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))

        await asyncio.gather(*[access_db() for _ in range(5)])