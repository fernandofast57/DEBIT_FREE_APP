
# Project Glossary

## Core Models & Services

### Account Related
- `User`: Main user entity containing authentication and profile details
- `MoneyAccount`: Euro currency account with precision(10,2)
- `GoldAccount`: Gold balance account with precision(10,4)
- `AccountStatus`: ['active', 'suspended', 'pending_verification']

### Noble System
- `NobleRank`: ['bronze', 'silver', 'gold', 'platinum']
- `NobleRelation`: Links users to their noble ranks
- `NobleStatus`: ['to_be_verified', 'verified', 'rejected']
- `NobleVerification`: Noble rank verification process

### Gold Management
- `GoldBar`: Physical gold tracking entity
- `GoldBarStatus`: ['available', 'reserved', 'distributed']
- `GoldTransformation`: Euro to gold conversion record
- `GoldFixingPrice`: Daily gold price from fixing API
- `TransformationStatus`: ['initiated', 'validated', 'processed', 'completed']

### Transaction & Operations
- `TransactionType`: ['purchase', 'sale', 'transfer', 'transformation']
- `TransactionStatus`: ['pending', 'processing', 'completed', 'failed']
- `OperationType`: ['user_action', 'system_event', 'time_based', 'condition_based']
- `ValidationStatus`: ['pending', 'approved', 'rejected']

### Security & Authentication
- `AuthToken`: JWT authentication token
- `TokenExpiration`: Token validity duration in hours
- `SecurityLevel`: ['standard', 'enhanced', 'maximum']
- `RateLimit`: Requests per minute limit
- `KycStatus`: ['pending', 'verified', 'rejected']

### Performance & Analytics
- `MetricsType`: ['daily_performance', 'weekly_performance', 'monthly_performance']
- `RiskMetrics`: ['market_risk', 'operational_risk', 'compliance_risk']
- `AnalyticsField`: ['roi', 'current_value', 'purchase_price', 'holding_period']
- `ReportType`: ['performance_summary', 'risk_report', 'trend_analysis']

### Service Names
- `AccountingService`: Handles financial accounting operations
- `TransformationService`: Manages gold conversion processes
- `BlockchainService`: Handles blockchain interactions
- `NobleSystemService`: Manages noble ranks and verifications
- `BonusDistributionService`: Handles bonus calculations and distribution
- `KycService`: Manages Know Your Customer processes
- `NotificationService`: Handles system notifications
- `SecurityService`: Manages authentication and authorization
- `MonitoringService`: System monitoring and metrics collection

### Database Configuration
- `MoneyPrecision`: Decimal(10,2) for euro amounts
- `GoldPrecision`: Decimal(10,4) for gold amounts
- `DatabaseUrl`: Connection string format
- `MigrationVersion`: Database migration version format

### API Endpoints
- `auth_bp`: Authentication endpoints '/auth/*'
- `gold_bp`: Gold operations '/gold/*'
- `noble_bp`: Noble system '/noble/*'
- `transformations_bp`: Transformations '/transformations/*'
- `accounting_bp`: Accounting '/accounting/*'
- `system_bp`: System operations '/system/*'

### Logging & Monitoring
- `LogLevel`: ['debug', 'info', 'warning', 'error', 'critical']
- `LogFormat`: Standard log entry format
- `MetricsFormat`: Performance metrics format
- `AlertType`: ['system', 'security', 'performance']
