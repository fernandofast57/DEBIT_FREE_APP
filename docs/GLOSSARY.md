# Gold Investment Platform Glossary

## Core Entities
- MoneyAccount: Euro balance management system for user accounts
- GoldTracking: Transaction tracking system for gold-related operations with full audit capabilities
- GoldAllocation: System for managing user gold allocations and tracking physical gold distribution
- User: Main user entity with authentication and profile data
- Transaction: Transaction entity for managing all financial operations and movements
- GoldTransformation: Manages the transformation of Euro to Gold with precision tracking and blockchain validation
- EuroAccount: Euro balance management with real-time conversion tracking
- GoldAccount: Gold balance management system with blockchain verification
- GoldAccount: Gold balance management with physical allocation tracking
- GoldTrace: Gold-Euro conversion registry with full audit trail
- GoldAllocation: User gold allocation management with batch tracking
- GoldBar: Physical gold bars registry with certification details
- Parameter: System configuration parameters with versioning
- KYCDetail: User identity verification with document management
- BonusTransaction: Bonus reward transactions with user association and tracking
- GoldReward: Gold-based reward management with precision tracking and user allocation
- NobleRelation: Management of noble rank relationships and hierarchies
- BonusRate: Bonus rate configuration for different noble levels
- Transaction: Core transaction entity for all financial operations
- GoldBar: Physical gold bar tracking and management system

## Noble System
- NobleRank: Noble rank management system
  - Bronze: Direct referral level (0.7% bonus) - First tier
  - Silver: Second level referrals (0.5% bonus) - Second tier
  - Gold: Third level referrals (0.5% bonus) - Top tier

## Operations
- WeeklyTransformation: Weekly gold transformation process with price fixing
- SpreadCalculation: Spread calculation (5% base + 1.7% operational)
- NobleCommission: Noble system commission distribution with multi-level tracking
- KYCValidation: User identity verification process with document validation

## Security
- AuthToken: JWT-based authentication token management
- TwoFactorValidation: Two-factor authentication with time-based OTP
- SecurityMonitoring: Real-time security monitoring system
- RateControl: Robust rate limiting system with Redis persistence and local fallback

## Monitoring
- PerformanceMetrics: System performance metrics with alerts
- TransactionTracking: Real-time transaction monitoring
- AuditLog: Comprehensive system audit logging
- BlockchainMonitor: Blockchain transaction verification
- TransformationMonitor: Gold transformation monitoring

## States and Types
- AccountStatus: ['active', 'suspended', 'verifying', 'to_verify']
- OperationType: ['gold_purchase', 'gold_sale', 'gold_transfer']
- OperationStatus: ['started', 'processing', 'completed', 'failed']
- ValidationStatus: ['pending', 'approved', 'rejected']
- KYCStatus: ['pending', 'approved', 'rejected']
- ContractStatus: ['not_sent', 'sent', 'signed']
- PAOStatus: ['inactive', 'activating', 'active']
- SEPAStatus: ['not_sent', 'pending', 'active']
- DocumentStatus: ['incomplete', 'verifying', 'verified', 'rejected']

## Formats and Precision
- GoldPrecision: Decimal(10,4)
- EuroPrecision: Decimal(10,2)
- IBANFormat: String(27)
- CustomerCodeFormat: String(10)
- TimestampFormat: ISO-8601

## System Constants
- OperationLimits: {
    'min_purchase': 100,
    'max_purchase': 100000,
    'min_sale': 1,
    'max_sale': 50000
}
- BatchIntervals: {
    'processing': 3600,
    'backup': 86400,
    'cleanup': 604800
}

## Utility Functions
- CurrencyConverter: Currency conversion utilities
- RewardCalculator: System rewards calculation
- DataValidator: Input data validation
- ReportGenerator: System report generation
- ErrorHandler: Centralized error handling