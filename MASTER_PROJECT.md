
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
└── logs/                  # Application logs
```

## Key Files
- `config.py`: Configuration settings using Replit Secrets
- `main.py`: Application entry point with logging setup
- `app/services/blockchain_service.py`: Polygon integration with retry mechanism
- `app/models/models.py`: Database models including noble ranks
- `blockchain/contracts/GoldSystem.sol`: Smart contract for gold system
- `blockchain/tests/NobleGoldSystem.test.js`: Smart contract test suite

## Recent Changes
1. Implemented secure configuration using Replit Secrets tool
2. Enhanced smart contract with noble ranks and bonus distribution
3. Added comprehensive test coverage for blockchain operations
4. Implemented batch transformation functionality
5. Added referral system tracking
6. Improved security with environment variables management

## Current Status

### Completed
- Project structure and configuration
- Database models and migrations
- Smart contract integration
- Smart contract test suite
- Noble ranks system
- Bonus distribution system
- Referral tracking system
- Batch transformation processing
- Secure secrets management with Replit Secrets

### Security Implementation
1. **Replit Secrets Integration**
   - SECRET_KEY for Flask
   - DATABASE_URL for database connection
   - CONTRACT_ADDRESS for blockchain
   - PRIVATE_KEY for transactions
   - RPC_ENDPOINTS for Polygon network

2. **Smart Contract Security**
   - Access control implementation
   - Secure transaction handling
   - Gas optimization
   - Batch processing

3. **Backend Security**
   - Environment variables through Secrets
   - Authentication middleware
   - Input validation
   - Transaction verification

### System Features
- Gold transformations
- Noble ranks progression
- Bonus distribution
- Referral tracking
- Batch operations
- Secure configuration management

## Testing
Smart contract tests:
```bash
npx hardhat test
```

Backend tests:
```bash
pytest tests/ -v
```

## Environment Setup
1. Configure Replit Secrets:
   - Add required keys in Tools -> Secrets
   - Access via os.environ in Python
   - Automatic encryption with AES-256
   - Secure key rotation

2. Local Development:
   - Uses Replit IDE
   - Hardhat for contract testing
   - SQLite database
   - Automated test suite
