
# Gold Investment Platform Usage Guide

## System Overview
The Gold Investment Platform allows users to:
- Transform money into gold investments
- Earn noble ranks based on investment levels
- Participate in bonus distribution
- Track investments on blockchain

## Authentication
1. Login using Replit authentication
2. System will automatically create required accounts

## Noble Ranks System
- Knight: Initial rank
- Baron: 50,000+ investment
- Count: 100,000+ investment
- Duke: 250,000+ investment

## API Endpoints
- POST /api/v1/transformations/transform
- POST /api/v1/transfers/process
- GET /api/v1/bonuses/calculate

## Security Features
- Rate limiting
- Secret rotation
- Multi-device support
- Blockchain validation

## Environment Setup
Required variables in .env:
```
SECRET_KEY=<secure-key>
DATABASE_URL=<db-url>
CONTRACT_ADDRESS=<address>
PRIVATE_KEY=<key>
RPC_ENDPOINTS=<endpoints>
```
