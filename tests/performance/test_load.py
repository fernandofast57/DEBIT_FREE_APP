
import pytest
import asyncio
import logging
from decimal import Decimal
from datetime import datetime
from app.services.transformation_service import TransformationService
from app.utils.monitoring.performance_monitor import PerformanceMonitor
from app.models.models import User, Transaction
from app.database import db

logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_concurrent_transformations(test_db):
    """Test system behavior under concurrent transformation requests"""
    try:
        service = TransformationService()
        tasks = []
        
        # Create test users
        users = []
        for i in range(5):
            user = User(username=f"load_test_user_{i}", 
                       email=f"loadtest{i}@example.com")
            users.append(user)
        
        db.session.add_all(users)
        await db.session.commit()
        
        # Run concurrent transformations
        for user in users:
            task = asyncio.create_task(
                service.process_transformation(
                    user_id=user.id,
                    euro_amount=Decimal('100.00'),
                    fixing_price=Decimal('50.00')
                )
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify results
        success_count = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'success')
        assert success_count == len(users), f"Expected {len(users)} successful transformations, got {success_count}"
        
    except Exception as e:
        logger.error(f"Error in concurrent transformations test: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_system_under_load(test_db):
    """Test system performance under heavy load"""
    monitor = PerformanceMonitor()
    service = TransformationService()
    
    try:
        # Create test user
        user = User(username="heavy_load_test", 
                   email="loadtest@example.com")
        db.session.add(user)
        await db.session.commit()
        
        # Execute batch operations
        start_time = datetime.now()
        
        for i in range(20):
            result = await service.process_transformation(
                user_id=user.id,
                euro_amount=Decimal('100.00'),
                fixing_price=Decimal('50.00')
            )
            monitor.record_metric('transformation_time', 
                               (datetime.now() - start_time).total_seconds())
            
            assert result['status'] == 'success', f"Transaction {i} failed"
            
        # Verify performance metrics
        metrics = monitor.get_metrics()
        avg_time = metrics['transformation_time']['average']
        assert avg_time < 1.0, f"Average transaction time ({avg_time}s) exceeds threshold"
        
    except Exception as e:
        logger.error(f"Error in load test: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_database_performance(test_db):
    """Test database performance under load"""
    try:
        # Batch insert test
        users = [User(username=f"perf_test_{i}", 
                     email=f"perf{i}@test.com") 
                for i in range(100)]
        
        start_time = datetime.now()
        db.session.add_all(users)
        await db.session.commit()
        
        insert_time = (datetime.now() - start_time).total_seconds()
        assert insert_time < 2.0, f"Batch insert took too long: {insert_time}s"
        
        # Query performance test
        start_time = datetime.now()
        result = await db.session.execute(
            "SELECT * FROM users WHERE username LIKE 'perf_test_%'"
        )
        query_time = (datetime.now() - start_time).total_seconds()
        
        assert query_time < 1.0, f"Query took too long: {query_time}s"
        assert len(result.all()) == 100, "Not all test users were retrieved"
        
    except Exception as e:
        logger.error(f"Error in database performance test: {str(e)}")
        raise
