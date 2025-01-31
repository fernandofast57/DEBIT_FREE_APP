
# Gold Investment Platform - Guida all'Uso

## Autenticazione
### Due Factor Authentication
```python
# Esempio di implementazione
from app.utils.security import ValidazioneDueFattori

auth = ValidazioneDueFattori()
code = auth.generate_code(user_id)
success = auth.verify_code(user_id, code)
```

### Rate Limiting
```python
from app.utils.security import RobustRateLimiter

limiter = RobustRateLimiter(redis_url="redis://localhost")
if limiter.is_allowed("user_123"):
    # Procedi con l'operazione
```

## Operazioni Oro
### Trasformazione
```python
from app.services import TracciatoOro

tracciato = TracciatoOro()
result = await tracciato.transform(
    user_id=123,
    amount=500.00,
    currency="EUR"
)
```

### Calcolo Spread
```python
from app.utils import SpreadCalcolo

spread = SpreadCalcolo()
final_price = spread.calculate(
    base_amount=500.00,
    operation_type="purchase"
)
```

## Sistema Nobile
### Calcolo Commissioni
```python
from app.services import CommissioneNobile

commission = CommissioneNobile()
bonus = commission.calculate(
    user_id=123,
    transaction_amount=1000.00
)
```

## Monitoraggio
### Performance Metrics
```python
from app.utils.monitoring import MetrichePerformance

metrics = MetrichePerformance()
metrics.track_operation("gold_purchase", duration=150)
metrics.track_error("validation_failed", details="Invalid amount")
```

## Prevenzione Errori
### Validazione Input
```python
from app.utils import ValidatoreDati

validator = ValidatoreDati()
is_valid = validator.validate_transaction({
    "amount": 500.00,
    "currency": "EUR"
})
```

## Best Practices
1. Utilizzare le costanti definite in OFFICIAL_STANDARDS.json
2. Implementare logging per tutte le operazioni critiche
3. Utilizzare le classi di validazione per ogni input
4. Monitorare le performance delle operazioni
5. Implementare fallback per servizi critici

## Sicurezza
1. Utilizzare sempre PreparedStatements per query SQL
2. Implementare protezione CSRF su tutti i form
3. Abilitare headers di protezione XSS
4. Utilizzare rate limiting su endpoint pubblici
5. Implementare audit logging per operazioni sensibili
