
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
│   ├── contracts/         # Smart contracts
│   └── scripts/           # Deployment scripts
├── migrations/            # Database migrations
├── tests/                 # Test suite
└── logs/                  # Application logs
```

## Key Files
- `config.py`: Configuration settings (DB, JWT, Blockchain, RPC endpoints)
- `main.py`: Application entry point with logging setup
- `app/services/blockchain_service.py`: Polygon integration with retry mechanism
- `app/models/models.py`: Database models including noble ranks
- `blockchain/contracts/GoldSystem.sol`: Smart contract for gold system

## Recent Changes
1. Implemented multiple RPC endpoints with failover
2. Enhanced logging system with rotation
3. Added noble ranks system
4. Implemented comprehensive test suite
5. Added retry mechanism for blockchain operations

## Current Status

### Completed
- Project structure and configuration
- Database models and migrations
- Smart contract integration
- Authentication system
- Noble ranks system
- Logging system with rotation
- Test environment setup

### Critical Points
1. **Blockchain Integration**
   - Multiple RPC endpoints with failover
   - Retry mechanism for failed transactions
   - Gas optimization

2. **Testing**
   - Local blockchain testing
   - Mock providers for tests
   - Integration test suite

3. **Security**
   - Authentication middleware
   - Token validation
   - Secure configuration management

4. **System Features**
   - Gold transformations
   - Bonus distribution
   - Batch collection
   - Noble ranks management

## Next Steps
1. Enhance error recovery in blockchain service
2. Implement additional noble rank features
3. Optimize batch processing performance
4. Add more comprehensive system tests

## Testing
Tests can be run using:
```bash
pytest tests/ -v
```

Local testing uses:
- SQLite in-memory database
- Mock blockchain provider
- Test fixtures for common scenarios
