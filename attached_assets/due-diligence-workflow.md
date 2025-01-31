# WORKFLOW DUE DILIGENCE E ONBOARDING CLIENTE

## 1. STRUTTURA DATI

```python
class CustomerOnboarding(db.Model):
    # Dati Personali
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    address = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    fiscal_code = db.Column(db.String(16))
    iban = db.Column(db.String(34))
    
    # Documenti
    id_card_front = db.Column(db.String(255))  # Path documento
    id_card_back = db.Column(db.String(255))
    fiscal_code_doc = db.Column(db.String(255))
    utility_bill = db.Column(db.String(255))
    
    # Stati verifiche
    verification_status = db.Column(db.String(20))  # da_verificare, verificato
    iban_verified = db.Column(db.Boolean, default=False)
    contract_status = db.Column(db.String(20))  # non_inviato, inviato, firmato
    
    # Piano Accumulo
    pao_status = db.Column(db.String(20))
    monthly_amount = db.Column(db.Decimal)
    sepa_status = db.Column(db.String(20))
```

## 2. WORKFLOW DETTAGLIATO

### 2.1 Registrazione Iniziale
```python
@app.route('/api/onboarding/register', methods=['POST'])
def register_customer():
    """
    1. Raccolta dati obbligatori:
       - Dati personali
       - Documenti identità
       - IBAN
    2. Creazione account 'da_verificare'
    3. Notifica team verifica
    """
```

### 2.2 Verifica Documenti
```python
class DocumentVerification:
    def verify_documents(self, customer_id):
        """
        1. Verifica autenticità documenti
        2. Controllo corrispondenza dati
        3. Validazione indirizzo su bolletta
        4. OCR documenti per cross-check
        """
```

### 2.3 Processo Consulenza
```python
class ConsultationProcess:
    def initiate_consultation(self, customer_id):
        """
        1. Assegnazione consulente
        2. Scheduling chiamata
        3. Guida bonifico verifica
        4. Preparazione contratto
        """
```

### 2.4 Verifica IBAN
```python
class IBANVerification:
    def verify_test_transfer(self, customer_id, transfer_data):
        """
        1. Ricezione bonifico test
        2. Verifica intestazione
        3. Validazione IBAN
        4. Aggiornamento stato account
        """
```

### 2.5 Gestione Contratto
```python
class ContractManagement:
    def handle_contract(self, customer_id):
        """
        1. Generazione contratto personalizzato
        2. Invio al cliente
        3. Tracking ricezione firma
        4. Attivazione account
        """
```

## 3. INTERFACCIA ADMIN

```jsx
const DueDiligenceAdmin = () => {
    return (
        <div className="admin-dashboard">
            {/* Pending Verifications */}
            <VerificationQueue 
                onVerify={handleVerification}
                onReject={handleRejection}
            />
            
            {/* Document Review */}
            <DocumentReview 
                onApprove={handleDocApproval}
                onRequest={handleAdditionalDocs}
            />
            
            {/* Contract Management */}
            <ContractTracking 
                onReceived={handleContractReceived}
                onActivate={handleAccountActivation}
            />
        </div>
    );
};
```

## 4. AUTOMAZIONI

### 4.1 Notifiche Automatiche
```python
class AutomatedNotifications:
    def send_notifications(self):
        """
        Notifiche per:
        1. Ricezione documenti
        2. Verifica completata
        3. Richiesta bonifico test
        4. Invio contratto
        5. Attivazione account
        """
```

### 4.2 Tracking Progressi
```python
class ProgressTracking:
    def track_progress(self, customer_id):
        """
        Monitoring:
        1. Stato documenti
        2. Verifica IBAN
        3. Firma contratto
        4. Setup PAO
        5. Attivazione SEPA
        """
```

## 5. GESTIONE PAO (Piano Accumulo Oro)

```python
class PAOManagement:
    def setup_pao(self, customer_id, amount):
        """
        1. Validazione importo
        2. Generazione modulo SEPA
        3. Tracking attivazione
        4. Setup acquisto automatico
        """
```

## 6. SICUREZZA E COMPLIANCE

```python
class ComplianceChecks:
    def verify_compliance(self, customer_id):
        """
        Verifiche:
        1. KYC/AML
        2. PEP check
        3. Sanction screening
        4. GDPR compliance
        """
```

## 7. CHECKLIST OPERATIVA

### 7.1 Pre-Verifica
- [ ] Ricezione documenti completi
- [ ] Validità documenti identità
- [ ] Corrispondenza indirizzi
- [ ] Validazione formato IBAN

### 7.2 Verifica Attiva
- [ ] Chiamata consulente effettuata
- [ ] Bonifico test ricevuto
- [ ] Intestazione conto verificata
- [ ] Contratto generato e inviato

### 7.3 Attivazione
- [ ] Contratto firmato ricevuto
- [ ] Account attivato
- [ ] Setup PAO completato
- [ ] SEPA attivato

## 8. FLOW TEMPORALE

```plaintext
1. Giorno 1: Registrazione iniziale
2. Giorno 1-2: Verifica documenti
3. Giorno 2-3: Chiamata consulente
4. Giorno 3-5: Bonifico test
5. Giorno 5-7: Processo contratto
6. Giorno 7+: Attivazione PAO
```

