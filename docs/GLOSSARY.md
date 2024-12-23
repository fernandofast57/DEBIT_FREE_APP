
# Project Glossary

## Core Models

### User Related
- `User`: Main user entity with authentication details
- `MoneyAccount`: User's fiat currency account
- `GoldAccount`: User's gold balance account
- `KYC`: Know Your Customer verification status

### Noble System
- `NobleRank`: Defines rank levels in the noble system
- `NobleRelation`: Manages relationships between users in noble system
- `NobleSystem`: Service class for noble system operations

### Gold Management
- `GoldBar`: Physical gold bar entity
- `GoldAllocation`: Links gold bars to user accounts
- `GoldReward`: Tracks gold rewards/bonuses
- `PAO`: Piano Accumulo Oro (Gold Accumulation Plan)
- `PPO`: Piano Protezione Oro (Gold Protection Plan)

### Transactions
- `Transaction`: Records all financial operations
- `SEPA`: Single Euro Payments Area transfer method

## Due Diligence Terms
- `verification_status`: KYC verification state ('pending', 'verified', 'rejected')
- `ibanHash`: Hashed IBAN for secure storage
- `support_transfer`: Initial transfer to verify account ownership
- `fixing_price`: Daily gold price fixing
- `CLIENT_SHARE`: Percentage of gold allocated to client (93.3%)
- `NETWORK_SHARE`: Percentage allocated to network (6.7%)

## Common Terms
- `balance`: Account balance (in EUR for MoneyAccount, grams for GoldAccount)
- `noble_rank`: User's current rank in noble system
- `verification_status`: KYC verification state
- `bonus_rate`: Rate for calculating noble system bonuses

## Service Names
- `NobleRankService`: Manages noble ranking operations
- `BlockchainService`: Handles blockchain interactions
- `AccountingService`: Manages financial operations
- `TransformationService`: Handles gold/money conversions
- `SecurityManager`: Manages security operations
- `RateLimiter`: Controls API request rates

## Status Codes
- `to_be_verified`: Initial account status
- `verified`: Confirmed account status
- `available`: Gold bar status
- `reserved`: Gold bar allocation status
- `distributed`: Gold bar distribution status
