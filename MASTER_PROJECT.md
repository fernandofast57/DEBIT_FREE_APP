
# GOLD INVESTMENT PLATFORM - Master Project Documentation

## System Architecture
```
├── app/                    # Main application code
│   ├── api/v1/            # API endpoints
│   ├── models/            # Database models
│   ├── routes/            # Web routes
│   ├── services/          # Business logic
│   └── utils/             # Utilities
├── blockchain/            # Blockchain integration
├── migrations/            # Database migrations
├── tests/                 # Test suite
└── logs/                  # Application logs
```

## Core Components

### Security Layer
- Environment validation
- Secret rotation system
- Rate limiting
- Multi-device support
- Advanced logging with rotation
- Blockchain address validation

### Noble System
- Rank progression system
- Investment tracking
- Bonus distribution
- Smart contract integration
- Automated rank updates

### API Endpoints
- /api/v1/transformations
- /api/v1/transfers
- /api/v1/bonuses

### Testing Infrastructure
- Unit tests
- Integration tests
- Multi-device testing
- Blockchain integration tests
- System flow tests

### Blockchain Integration
- Smart contract deployment
- Transaction management
- Multiple RPC endpoints
- Retry mechanism
- Noble ranks tracking

## Configuration
Required environment variables:
```
SECRET_KEY=<secure-key>
DATABASE_URL=<db-url>
CONTRACT_ADDRESS=<address>
PRIVATE_KEY=<key>
RPC_ENDPOINTS=<endpoints>
```

## Recent Updates
1. Rate limiting implementation
2. Enhanced security validation
3. Multi-device support
4. Advanced logging system
5. Noble ranks optimization
6. Smart contract upgrades

## Testing
```bash
pytest tests/ -v
pytest tests/integration/ -v
pytest tests/test_noble_system.py -v
```

## Security Features
- Rate limiting protection
- Secret rotation
- Environment validation
- Secure logging
- Multi-device authentication
- Blockchain validation

## System Status
✅ Core functionality
✅ Security features
✅ Noble ranks system
✅ Smart contracts
✅ Testing suite
✅ Documentation
