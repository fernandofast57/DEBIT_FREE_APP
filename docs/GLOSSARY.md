
# Gold Investment Platform Glossary

## Core Entities

### Account Management
- EuroAccount: Primary euro currency account with high precision balance tracking (Decimal 10,2), manages user deposits and withdrawals
- MoneyAccount: Euro balance management with precision tracking (Decimal 10,2)
- GoldAccount: Gold balance management with blockchain verification (Decimal 10,4)
- User: Main user entity with authentication and KYC data
- KYCDetail: User identity verification details including document type, status and verification timestamps

### Transaction Management
- Transaction: Core transaction entity for all financial operations
- GoldTransformation: Euro to Gold transformation with blockchain validation
- BonusTransaction: Noble system bonus distribution tracking

### Gold Management
- GoldAllocation: Physical gold allocation tracking system
- GoldBar: Physical gold bars registry with certification
- GoldTracking: Full audit trail for gold operations

### Noble System
- NobleRelation: Management of noble rank relationships
- BonusRate: Configurable bonus rates per noble level
- NobleRank: Noble rank management system
  - Bronze: Direct referrals (0.7% bonus)
  - Silver: Second level (0.5% bonus)
  - Gold: Third level (0.5% bonus)

## Operations

### Core Processes
- WeeklyTransformation: Weekly gold fixing and transformation
- SpreadCalculation: Base spread (5%) + operational (1.7%)
- NobleCommission: Multi-level commission distribution

### Validation
- KYCValidation: Identity verification process
- BlockchainValidation: Transaction verification on chain
- TransactionValidation: Financial operation validation

## Security

### Authentication
- AuthToken: JWT-based authentication
- TwoFactorValidation: Time-based OTP security
- RateControl: Redis-based rate limiting

### Monitoring
- SecurityMonitoring: Real-time security tracking
- PerformanceMetrics: System performance tracking
- AuditLog: Comprehensive operation logging
- BlockchainMonitor: Chain transaction verification

## States and Types

### Account States
- AccountStatus: ['active', 'suspended', 'verifying', 'to_verify']
- KYCStatus: ['pending', 'approved', 'rejected']
- DocumentStatus: ['incomplete', 'verifying', 'verified', 'rejected']

### Operation States
- OperationType: ['gold_purchase', 'gold_sale', 'gold_transfer']
- OperationStatus: ['started', 'processing', 'completed', 'failed']
- ValidationStatus: ['pending', 'approved', 'rejected']
- ContractStatus: ['not_sent', 'sent', 'signed']
- PAOStatus: ['inactive', 'activating', 'active']
- SEPAStatus: ['not_sent', 'pending', 'active']

## Technical Specifications

### Precision
- GoldPrecision: Decimal(10,4)
- EuroPrecision: Decimal(10,2)

### Formats
- IBANFormat: String(27)
- CustomerCodeFormat: String(10)
- TimestampFormat: ISO-8601

### System Configuration
- Parameter: System configuration entity storing key-value pairs for application settings

### System Limits
- OperationLimits:
  - min_purchase: 100
  - max_purchase: 100000
  - min_sale: 1
  - max_sale: 50000

- BatchIntervals:
  - processing: 3600
  - backup: 86400
  - cleanup: 604800

## Utility Functions
- CurrencyConverter: Currency conversion utilities
- RewardCalculator: Noble system rewards calculation
- DataValidator: Input data validation
- ErrorHandler: Centralized error management
- BlockchainValidator: Chain transaction validation
- MetricsCollector: System performance tracking
