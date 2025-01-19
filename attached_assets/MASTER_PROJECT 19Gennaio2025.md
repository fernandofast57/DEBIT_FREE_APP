# Gold Investment Platform - Master Reference Document

## 1. Visione Complessiva

### 1.1 Obiettivo
Creare una piattaforma di investimento in oro che permetta:
- Accumulo settimanale tramite bonifici ricorrenti
- Trasformazione automatica euro→oro ogni martedì al fixing delle 15:00
- Sistema di affiliazione a tre livelli (0,7% - 0,5% - 0,5%) con titoli nobiliari premiati in oro fino equivalente a 1,7% oro distribuito
- Tracciamento trasparente tramite blockchain Polygon
- Gestione efficiente dello spread (5% Struttura 1.7% Rete)

### 1.2 Core Values
- Sicurezza e compliance bancaria
- Trasparenza delle operazioni
- Semplicità d'uso
- Scalabilità e performance

## 2. Architettura Tecnica

### 2.1 Stack Tecnologico
- **Backend**: Flask + PostgreSQL + Redis
- **Frontend**: React + TailwindUI + shadcn/ui
- **Blockchain**: Polygon Network + Smart Contracts
- **Infrastructure**: Replit + Docker + Kubernetes

### 2.2 Componenti Core
1. **AuthSystem**
   - KYC e verifica documenti
   - Due diligence
   - 2FA obbligatorio
   - Gestione sessioni sicure
   - Due Diligence di riconoscimento e certificazione delle identità (Richiesto dalla Banca d'Italia per normativa antiriciclaggio)

2. **MoneySystem**
   - Gestione bonifici ricorrenti
   - Verifica IBAN
   - Tracking pagamenti
   - Notifiche automatiche

3. **GoldSystem**
   - Trasformazione settimanale
   - Calcolo fixing
   - Gestione spread
   - Tracking possesso oro

4. **AffiliateSystem**
   - Titoli nobiliari
   - Calcolo commissioni
   - Genealogia network
   - Distribuzione bonus

## 3. Database Schema

### 3.1 Core Tables
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    kyc_status VARCHAR(50),
    noble_rank VARCHAR(50)
);

CREATE TABLE money_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    balance DECIMAL(15,2),
    last_transfer TIMESTAMP
);

CREATE TABLE gold_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    balance_grams DECIMAL(15,4),
    last_transformation TIMESTAMP
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    type VARCHAR(50),
    amount DECIMAL(15,2),
    status VARCHAR(50),
    created_at TIMESTAMP
);
```

## 4. API Endpoints

### 4.1 Auth Endpoints
```plaintext
POST /api/auth/register
POST /api/auth/login
POST /api/auth/verify-2fa
POST /api/auth/kyc/upload
```

### 4.2 Money Endpoints
```plaintext
POST /api/money/setup-transfer
GET /api/money/balance
GET /api/money/transactions
POST /api/money/verify-iban
```

### 4.3 Gold Endpoints
```plaintext
GET /api/gold/balance
GET /api/gold/transactions
GET /api/gold/fixing-price
POST /api/gold/transform
```

### 4.4 Affiliate Endpoints
```plaintext
GET /api/affiliate/network
GET /api/affiliate/commissions
GET /api/affiliate/rank
POST /api/affiliate/invite
```

## 5. Smart Contracts

### 5.1 GoldTransformation Contract
```solidity
contract GoldTransformation {
    struct Transaction {
        uint32 timestamp;
        uint96 euroAmount;
        uint96 goldAmount;
        uint32 fixingPrice;
    }
    
    function batchTransform(
        address[] calldata users,
        uint96[] calldata amounts,
        uint32 fixingPrice
    ) external {
        // Batch processing logic
    }
}
```

## 6. Sicurezza e Compliance

### 6.1 Security Framework
- HTTPS obbligatorio
- Rate limiting
- Input validation
- SQL injection protection
- XSS protection
- CSRF protection

### 6.2 GDPR Compliance
- Data minimization
- Explicit consent
- Right to be forgotten
- Data encryption
- Audit logging

## 7. Development Flow

### 7.1 Setup Locale
```bash
# Clone repository
git clone [repository-url]

# Setup Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup React environment
cd frontend
npm install
```

### 7.2 Deployment
```bash
# Build frontend
cd frontend
npm run build

# Deploy backend
docker build -t gold-platform .
docker push gold-platform
```

## 8. Testing Strategy

### 8.1 Unit Tests
- Auth system tests
- Money system tests
- Gold system tests
- Affiliate system tests

### 8.2 Integration Tests
- API endpoint tests
- Database integration tests
- Blockchain integration tests
- Payment system tests

## 9. Monitoring

### 9.1 Key Metrics
- Transaction success rate
- System performance
- Blockchain costs
- User engagement

### 9.2 Alerting
- Transaction failures
- System errors
- Security incidents
- Performance degradation

## 10. Maintenance

### 10.1 Regular Tasks
- Database backup
- Log rotation
- Security updates
- Performance optimization

### 10.2 Emergency Procedures
- System rollback
- Database restore
- Blockchain fallback
- Communication plan

## 11. Future Enhancements

### 11.1 Planned Features
- Mobile app
- Advanced analytics
- Additional payment methods
- Enhanced gamification

### 11.2 Technical Debt
- Code refactoring
- Test coverage
- Documentation updates
- Performance optimization

---

Document Version: 1.0
Last Updated: 2025-01-19