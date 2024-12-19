
# GOLD INVESTMENT PLATFORM - Master Project Documentation

## Directory Structure
```
├── app/                    # Main application code
│   ├── api/v1/            # API endpoints for bonuses, transfers, transformations
│   ├── models/            # Database models including noble system
│   ├── routes/            # Web routes for auth, gold, affiliate
│   ├── services/          # Business logic services
│   └── utils/             # Utility functions
├── blockchain/            # Blockchain integration
│   ├── contracts/         # Smart contracts including NobleGoldSystem
│   ├── tests/            # Smart contract tests
│   └── scripts/           # Deployment scripts
├── migrations/            # Database migrations
├── tests/                 # Test suite
│   ├── integration/       # Integration tests
│   ├── unit/             # Unit tests
│   └── conftest.py       # Test fixtures and configuration
└── logs/                  # Application logs
```

## Key Files
- `config.py`: Configuration settings using Replit Secrets
- `main.py`: Application entry point with logging setup
- `app/services/blockchain_service.py`: Polygon integration with retry mechanism
- `app/models/models.py`: Database models including noble ranks
- `blockchain/contracts/GoldSystem.sol`: Smart contract for gold system
- `tests/conftest.py`: Test fixtures including mock environment variables

## Recent Changes
1. Implementato sistema di logging con RotatingFileHandler
2. Aggiunto supporto per mock dei secrets nei test
3. Migliorata gestione delle variabili d'ambiente con dotenv
4. Implementato sistema di retry per le operazioni blockchain
5. Aggiunta validazione della configurazione all'avvio
6. Migliorata struttura dei test con fixtures dedicati

## Current Status

### Completed
- Configurazione sicura con Replit Secrets
- Sistema di logging avanzato
- Test suite completa con mock
- Gestione errori e retry per blockchain
- Validazione configurazione
- Integrazione con Polygon
- Sistema Noble ranks

### Security Implementation
1. **Environment Variables**
   - Gestione sicura con python-dotenv
   - Validazione all'avvio
   - Mock per testing
   - Rotazione sicura dei secrets

2. **Logging**
   - RotatingFileHandler per gestione log
   - Backup automatico dei log
   - Formattazione standardizzata
   - Livelli di log configurabili

3. **Testing**
   - Mock dei secrets per test
   - Fixtures pytest
   - Test di integrazione
   - Test unitari

### System Features
- Gold transformations
- Noble ranks system
- Bonus distribution
- Blockchain integration
- Secure configuration
- Comprehensive logging

## Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test category
pytest tests/unit/ -v
pytest tests/integration/ -v
```

## Environment Setup
1. Required Environment Variables:
   ```
   SECRET_KEY=<secure-random-key>
   DATABASE_URL=<database-url>
   CONTRACT_ADDRESS=<contract-address>
   PRIVATE_KEY=<private-key>
   RPC_ENDPOINTS=<endpoints>
   ```

2. Local Development:
   - Uses Replit IDE
   - SQLite database
   - Automated test suite
   - Logging system
