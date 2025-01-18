
import pytest
import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from app.services.transformation_service import TransformationService
from app.utils.monitoring.performance_monitor import PerformanceMonitor
from app.database import db
from app.models.models import User, Transaction

logger = logging.getLogger(__name__)

class PerformanceTest:
    def __init__(self):
        self.monitor = PerformanceMonitor()
        self.service = TransformationService()

    async def setup_test_data(self):
        """Preparazione dati di test"""
        users = []
        for i in range(10):
            user = User(
                username=f"perf_test_{i}",
                email=f"perf{i}@test.com"
            )
            users.append(user)
        
        db.session.add_all(users)
        await db.session.commit()
        return users

@pytest.mark.asyncio
async def test_concurrent_transformations(test_db):
    """Test delle trasformazioni concorrenti"""
    perf_test = PerformanceTest()
    
    try:
        users = await perf_test.setup_test_data()
        start_time = datetime.now()
        
        tasks = [
            perf_test.service.process_transformation(
                user_id=user.id,
                euro_amount=Decimal('100.00'),
                fixing_price=Decimal('50.00')
            ) for user in users
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Verifica risultati
        success_count = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'success')
        perf_test.monitor.record_metric('transformation_success_rate', success_count / len(users))
        perf_test.monitor.record_metric('average_execution_time', execution_time / len(users))
        
        assert success_count >= len(users) * 0.9, f"Success rate below 90%: {success_count}/{len(users)}"
        assert execution_time < 5.0, f"Total execution time too high: {execution_time}s"
        
    except Exception as e:
        logger.error(f"Error in concurrent transformation test: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_database_performance(test_db):
    """Test delle performance del database"""
    perf_test = PerformanceTest()
    
    try:
        start_time = datetime.now()
        users = await perf_test.setup_test_data()
        setup_time = (datetime.now() - start_time).total_seconds()
        
        # Test query performance
        start_time = datetime.now()
        result = await db.session.execute(
            "SELECT * FROM users WHERE username LIKE 'perf_test_%'"
        )
        query_time = (datetime.now() - start_time).total_seconds()
        
        # Record metriche
        perf_test.monitor.record_metric('db_setup_time', setup_time)
        perf_test.monitor.record_metric('db_query_time', query_time)
        
        assert setup_time < 2.0, f"Database setup too slow: {setup_time}s"
        assert query_time < 1.0, f"Query execution too slow: {query_time}s"
        assert len(result.all()) == 10, "Not all test users were retrieved"
        
    except Exception as e:
        logger.error(f"Error in database performance test: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_system_load(test_db):
    """Test del carico di sistema"""
    perf_test = PerformanceTest()
    
    try:
        user = User(username="load_test", email="load@test.com")
        db.session.add(user)
        await db.session.commit()
        
        metrics = []
        for _ in range(20):
            start_time = datetime.now()
            result = await perf_test.service.process_transformation(
                user_id=user.id,
                euro_amount=Decimal('100.00'),
                fixing_price=Decimal('50.00')
            )
            execution_time = (datetime.now() - start_time).total_seconds()
            metrics.append(execution_time)
            
            assert result['status'] == 'success', f"Transaction failed: {result}"
        
        avg_time = sum(metrics) / len(metrics)
        perf_test.monitor.record_metric('avg_transaction_time', avg_time)
        assert avg_time < 0.5, f"Average transaction time too high: {avg_time}s"
        
    except Exception as e:
        logger.error(f"Error in system load test: {str(e)}")
        raise
