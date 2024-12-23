# Project Glossary

## Core Models

### User Related
- `User`: Main user entity with authentication details
- `MoneyAccount`: User's fiat currency account
- `GoldAccount`: User's gold balance account
- `NobleRelation`: User's noble rank and verification status

### Noble System
- `NobleRank`: Defines rank levels and bonus rates in the noble system
- `NobleRelation`: Manages relationships between users and noble ranks
- `NobleSystem`: Service class for noble system operations

### Gold Management
- `GoldBar`: Physical gold bar entity
- `GoldAllocation`: Links gold bars to user accounts
- `GoldReward`: Tracks gold rewards/bonuses
- `Transaction`: Records all financial operations

## Due Diligence Terms
- `verification_status`: KYC verification state ('to_be_verified', 'verified', 'rejected')
- `document_type`: Type of verification document
- `document_number`: Verification document identifier
- `verification_date`: Date of verification completion
- `fixing_price`: Daily gold price fixing

## Common Terms
- `balance`: Account balance (in EUR for MoneyAccount, grams for GoldAccount)
- `bonus_rate`: Rate for calculating noble system bonuses
- `level`: Noble rank hierarchy level
- `title`: Noble rank title

## Service Names
- `NobleSystem`: Manages noble system operations
- `SecurityManager`: Manages security operations
- `APP_NAME`: Application identifier used for logging and security tracking (default: 'gold-investment')
- `RobustRateLimiter`: Redis-backed rate limiting system with configurable window sizes and request limits
- `rate_limit`: Decorator for endpoint-specific rate limiting
- `redis_url`: Connection string for Redis (default: "redis://localhost:6379/0")
- `window_size`: Time window for rate limiting (default: 60 seconds)
- `max_requests`: Maximum allowed requests per window (default: 100)

## Status Codes
- `to_be_verified`: Initial verification status
- `verified`: Confirmed verification status
- `rejected`: Failed verification status
- `available`: Gold bar status
- `reserved`: Gold bar allocation status
- `distributed`: Gold bar distribution status