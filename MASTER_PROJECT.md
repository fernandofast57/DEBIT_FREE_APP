
# GOLD INVESTMENT PLATFORM - Master Project Documentation

## Directory Structure
```
├── app/                    # Main application code
│   ├── api/v1/            # API endpoints for bonuses, transfers, transformations
│   ├── models/            # Database models including noble system
│   ├── routes/            # Web routes for auth, gold, affiliate
│   ├── services/          # Business logic services
│   └── utils/             # Utility functions and security
├── blockchain/            # Blockchain integration
│   ├── contracts/         # Smart contracts including NobleGoldSystem
│   ├── tests/            # Smart contract tests
│   └── scripts/          # Deployment scripts
├── migrations/            # Database migrations
├── tests/                # Test suite
│   ├── integration/      # Integration tests
│   ├── unit/            # Unit tests
│   ├── config/          # Test configurations
│   └── conftest.py      # Test fixtures and configuration
└── logs/                # Application logs
```

## Key Components

### Configuration System
- Enhanced environment validation
- Secure secret management
- Automated secret rotation
- Advanced logging with file rotation
- Multi-environment support

### Security Features
- Environment variable validation
- Contract address format verification
- Private key validation
- RPC endpoint security checks
- Database URL validation
- Secret rotation mechanism
- Comprehensive logging system

### Testing Infrastructure
- Multi-device testing support
- Device-specific configurations
- Integration tests
- Unit tests
- Blockchain integration tests

### Blockchain Integration
- Smart contract interaction
- Multiple RPC endpoint support
- Retry mechanism with fallback
- Transaction validation
- Noble ranks system

## Core Features
- Gold transformations
- Noble ranks system
- Bonus distribution
- Affiliate management
- Secure configuration
- Advanced logging
- Multi-device support

## Environment Setup
Required Environment Variables:
```
SECRET_KEY=<secure-random-key>
DATABASE_URL=<database-url>
CONTRACT_ADDRESS=<contract-address>
PRIVATE_KEY=<private-key>
RPC_ENDPOINTS=<comma-separated-endpoints>
```

## Running Tests
```bash
# All tests
pytest tests/ -v

# Specific categories
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/test_multi_device.py -v
```

## Recent Improvements
1. Added multi-device testing capabilities
2. Implemented secret rotation system
3. Enhanced configuration validation
4. Improved blockchain interaction reliability
5. Added comprehensive logging
6. Implemented secure secret management

## Security Implementation
1. Configuration Validation
   - Environment variable verification
   - Format validation for blockchain addresses
   - Secure endpoint validation
   - Database URL verification

2. Advanced Logging
   - Rotating file handler
   - Structured log format
   - Multiple log levels
   - Automated backup

3. Secret Management
   - Automated rotation
   - Secure storage
   - Validation checks
   - Testing support

## System Status
- ✅ Secure configuration
- ✅ Advanced logging
- ✅ Multi-device testing
- ✅ Blockchain integration
- ✅ Noble ranks system
- ✅ Secret rotation
- ✅ Comprehensive validation
