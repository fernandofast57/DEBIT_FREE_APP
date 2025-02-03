
# Gold Investment Platform - Guida all'Uso

## Autenticazione e Sicurezza

### Due Factor Authentication
```python
from app.utils.security import ValidazioneDueFattori

auth = ValidazioneDueFattori()
code = auth.generate_code(user_id)
success = auth.verify_code(user_id, code)
```

### Rate Limiting
```python
from app.utils.security.robust_rate_limiter import RobustRateLimiter

limiter = RobustRateLimiter(redis_url="redis://0.0.0.0:6379")
if limiter.is_allowed("user_123", "api_requests"):
    # Procedi con l'operazione
```

## Due Diligence

### Document Validation
```python
from app.services.kyc_service import KYCService

kyc = KYCService()
status = await kyc.validate_documents({
    'id_front': id_front_file,
    'id_back': id_back_file,
    'utility_bill': utility_bill_file,
    'tax_id': tax_id_file
})
```

### IBAN Validation
```python
from app.services.payment_service import PaymentService

payment = PaymentService()
validation = await payment.verify_iban(
    iban="IT60X0542811101000000123456",
    test_amount=0.01
)
```

## Gold Operations

### Transformation
```python
from app.services.transformation_service import TransformationService

service = TransformationService()
result = await service.transform(
    user_id=123,
    amount=500.00,
    currency="EUR",
    fixing_price=59.17
)
```

### Weekly Processing
```python
from app.services.weekly_processing_service import WeeklyProcessingService

processor = WeeklyProcessingService()
status = await processor.process_weekly_transformations()
```

## Noble System

### Bonus Distribution
```python
from app.services.bonus_distribution_service import BonusDistributionService

distribution = BonusDistributionService()
bonus = await distribution.calculate_and_distribute(
    transaction_id="tr_123",
    amount=1000.00
)
```

### Noble Rank Management
```python
from app.services.noble_rank_service import NobleRankService

noble = NobleRankService()
rank = await noble.update_rank(user_id=123)
```

## Monitoring & Analytics

### Performance Monitoring
```python
from app.utils.monitoring import MetrichePerformance

metrics = MetrichePerformance()
metrics.track_operation("gold_purchase", duration=150)
metrics.track_error("validation_failed", details="Invalid amount")
```

### System Health
```python
from app.utils.monitoring import SystemHealth

health = SystemHealth()
status = health.check_all_services()
```

### Blockchain Monitoring
```python
from app.utils.monitoring import BlockchainMonitor

monitor = BlockchainMonitor()
status = await monitor.verify_transaction(tx_hash="0x123...")
```

## Security Best Practices

1. Input Validation
```python
from app.utils.validation import DataValidator

validator = DataValidator()
is_valid = validator.validate_transaction({
    "amount": 500.00,
    "currency": "EUR"
})
```

2. Error Handling
```python
from app.core.exceptions import GoldInvestmentError

try:
    result = await service.process()
except GoldInvestmentError as e:
    logger.error(f"Processing error: {str(e)}")
    # Handle error appropriately
```

## Response Time Standards
- Database queries: < 50ms
- API endpoints: < 150ms
- Blockchain verification: < 5s
- Security checks: < 30ms

## Security Thresholds
- Maximum login attempts: 5 per hour
- Session timeout: 24 hours
- Password complexity: 12 chars minimum
- Key rotation: 90 days

## Due Diligence Timeframes
- Document review: < 48 hours
- IBAN verification: < 72 hours
- Contract processing: < 48 hours
- KYC completion: < 5 business days

## Best Practices
1. Follow security standards in SECURITY_AUDIT.md
2. Implement proper error logging
3. Use rate limiting for all public endpoints
4. Monitor blockchain transactions
5. Keep documentation updated
6. Follow development standards in DEVELOPMENT_STANDARDS.md
7. Use proper error boundaries
8. Implement comprehensive testing

## Error Codes
Standard HTTP status codes are used:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

## Rate Limits
As defined in OFFICIAL_STANDARDS.json:
- API requests: 50/minute
- Login attempts: 5/hour
- Blockchain operations: 10/minute

## Monitoring Setup
1. Configure logging
```python
from app.utils.monitoring import LoggingManager

logger = LoggingManager.setup_logger("service_name")
logger.info("Operation completed successfully")
```

2. Performance tracking
```python
from app.utils.monitoring import PerformanceMonitor

monitor = PerformanceMonitor()
monitor.track_api_response_time("/api/v1/gold/transform", 145)
```

3. Alert system
```python
from app.utils.monitoring import AlertSystem

alerts = AlertSystem()
alerts.trigger_alert("high_latency", "API response time exceeding threshold")
```
