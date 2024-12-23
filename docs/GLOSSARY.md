
# Project Glossary

## Core Models

### User Related
- `User`: Main user entity with authentication details
- `MoneyAccount`: User's fiat currency account
- `GoldAccount`: User's gold balance account

### Noble System
- `NobleRank`: Defines rank levels in the noble system
- `NobleRelation`: Manages relationships between users in noble system
- `NobleSystem`: Service class for noble system operations

### Gold Management
- `GoldBar`: Physical gold bar entity
- `GoldAllocation`: Links gold bars to user accounts
- `GoldReward`: Tracks gold rewards/bonuses

### Transactions
- `Transaction`: Records all financial operations

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
