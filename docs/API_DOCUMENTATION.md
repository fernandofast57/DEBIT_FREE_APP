
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
- Request:
```json
{
    "user_id": 123,
    "amount": 500.0
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
