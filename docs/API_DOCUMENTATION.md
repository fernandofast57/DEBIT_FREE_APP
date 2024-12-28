
# 📚 Gold Investment Platform API Documentation

## 🚀 Core Endpoints

### 🛡️ Authentication

#### 1. Register User
- `POST /api/v1/auth/register`
- Request:
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securePassword123"
}
```

#### 2. Login User
- `POST /api/v1/auth/login`
- Request:
```json
{
    "email": "john@example.com",
    "password": "securePassword123"
}
```

#### 3. Verify 2FA
- `POST /api/v1/auth/verify-2fa`
- Request:
```json
{
    "user_id": 123,
    "code": "123456"
}
```

### 💰 Transformations

#### Weekly Gold Transformation
- `POST /api/v1/transformations/transform`
- **Description:** Transforms user's money into gold at Tuesday's 15:00 fixing price
- **Authentication:** Required (JWT Token)
- **Request Body:**
```json
{
    "user_id": 123,
    "amount": 500.0,
    "currency": "EUR"
}
```
- **Response:**
```json
{
    "success": true,
    "data": {
        "transaction_id": "tr_123456",
        "gold_grams": 8.45,
        "fixing_price": 59.17,
        "fee_amount": 33.5,
        "status": "completed",
        "timestamp": "2024-01-23T15:00:00Z"
    },
    "message": "Transformation completed successfully"
}
```
- **Error Responses:**
  - 400: Invalid amount or currency
  - 401: Unauthorized
  - 403: Insufficient balance
  - 429: Rate limit exceeded
  - 500: Processing error

#### Get Transformation Status
- `GET /api/v1/transformations/status/{transaction_id}`
- **Description:** Retrieves the status of a specific transformation
- **Authentication:** Required
- **Response:**
```json
{
    "success": true,
    "data": {
        "transaction_id": "tr_123456",
        "status": "completed",
        "details": {
            "gold_grams": 8.45,
            "fixing_price": 59.17
        }
    }
}
```

### 👑 Noble System

#### Get Current Rank
- `GET /api/v1/noble/rank`
- Query: `user_id=123`

#### Get Bonus History
- `GET /api/v1/noble/bonuses`
- Query: `user_id=123`

### 🧾 Accounting

#### Get Balance
- `GET /api/v1/accounting/balance`
- Query: `user_id=123`

#### Get Transactions
- `GET /api/v1/accounting/transactions`
- Query: `user_id=123`

## Response Format
```json
{
    "success": boolean,
    "data": object,
    "message": string
}
```

## Error Codes
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

## Best Practices
1. Use JWT token in Authorization header
2. Respect rate limits
3. Handle errors appropriately
4. Use HTTPS for all requests
