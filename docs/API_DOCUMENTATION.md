
# Gold Investment Platform API Documentation

## Authentication

### Register [POST /api/v1/auth/register]
- Description: Register a new user
- Authentication: Not required
- Request Body:
```json
{
    "email": "user@example.com",
    "password": "securePassword123",
    "name": "Mario Rossi",
    "tax_code": "RSSMRA80A01H501U"
}
```
- Response (200):
```json
{
    "success": true,
    "data": {
        "user_id": "123",
        "email": "user@example.com",
        "name": "Mario Rossi",
        "created_at": "2024-01-29T10:00:00Z"
    }
}
```

### Login [POST /api/v1/auth/login]
- Description: Authenticate an existing user
- Authentication: Not required
- Request Body:
```json
{
    "email": "user@example.com",
    "password": "securePassword123"
}
```
- Response (200):
```json
{
    "success": true,
    "data": {
        "access_token": "eyJhbGciOiJ...",
        "refresh_token": "eyJhbGciOiJ...",
        "expires_in": 3600
    }
}
```

## Gold Operations

### Transform Euro to Gold [POST /api/v1/oro/trasforma]
- Description: Transform Euro to physical gold
- Authentication: Required (Bearer Token)
- Rate Limit: 50 requests/hour
- Request Body:
```json
{
    "euro_amount": 500.00,
    "fixing_price": 59.17
}
```
- Response (200):
```json
{
    "success": true,
    "data": {
        "transaction_id": "tr_123456",
        "gold_grams": 8.45,
        "price_per_gram": 59.17,
        "total_cost": 500.0,
        "status": "completed",
        "timestamp": "2024-01-29T10:15:00Z"
    }
}
```

### Transform Gold to Euro [POST /api/v1/oro/da_euro]
- Description: Transform gold back to Euro
- Authentication: Required (Bearer Token)
- Request Body:
```json
{
    "gold_grams": 8.45,
    "fixing_price": 59.17
}
```
- Response (200):
```json
{
    "success": true,
    "data": {
        "transaction_id": "tr_123457",
        "euro_amount": 500.00,
        "price_per_gram": 59.17,
        "status": "completed",
        "timestamp": "2024-01-29T10:20:00Z"
    }
}
```

### Get Gold Balance [GET /api/v1/saldo]
- Description: Get user's current gold balance
- Authentication: Required (Bearer Token)
- Response (200):
```json
{
    "success": true,
    "data": {
        "balance": 8.45,
        "last_update": "2024-01-29T10:15:00Z"
    }
}
```

## Noble System

### Get Noble Rank [GET /api/v1/noble/rank]
- Description: Gets the user's current noble rank
- Authentication: Required (Bearer Token)
- Response (200):
```json
{
    "success": true,
    "data": {
        "current_rank": "bronze",
        "commission_rate": 0.7,
        "referrals_count": 3,
        "total_volume": 1500.0,
        "next_rank": "silver"
    }
}
```

### Get Rank Requirements [GET /api/v1/noble/requirements]
- Description: Get requirements for all noble ranks
- Authentication: Required (Bearer Token)
- Response (200):
```json
{
    "success": true,
    "data": [
        {
            "level": 1,
            "bonus_rate": 0.007
        },
        {
            "level": 2,
            "bonus_rate": 0.005
        },
        {
            "level": 3,
            "bonus_rate": 0.005
        }
    ]
}
```

## Error Responses

### 400 Bad Request
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input parameters",
        "details": ["Amount must be greater than 100 EUR"]
    }
}
```

### 401 Unauthorized
```json
{
    "success": false,
    "error": {
        "code": "UNAUTHORIZED",
        "message": "Authentication required"
    }
}
```

### 429 Too Many Requests
```json
{
    "success": false,
    "error": {
        "code": "RATE_LIMIT_EXCEEDED",
        "message": "Too many requests",
        "retry_after": 3600
    }
}
```

## Best Practices
1. Use HTTPS for all requests
2. Include the JWT token in the Authorization header
3. Handle errors appropriately
4. Respect rate limits
5. Implement retry with exponential backoff
