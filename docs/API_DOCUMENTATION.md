
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
### Purchase Gold [POST /api/v1/gold/purchase]
- Description: Purchase physical gold
- Authentication: Required (Bearer Token)
- Rate Limit: 50 requests/hour
- Request Body:
```json
{
    "amount": 500.00,
    "currency": "EUR"
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

## Noble System

The platform implements a multi-level affiliate marketing system where users are rewarded based on the gold purchases made within their network.

### Key Features:
- Unlimited levels in the affiliate network structure
- Three bonus tiers:
  - Bronze: Level 1 (direct referrals) - 0.7% bonus
  - Silver: Level 2 (referrals of referrals) - 0.5% bonus
  - Gold: Level 3 (referrals of referrals of referrals) - 0.5% bonus
- Unlimited direct referrals per user
- Bonuses calculated on gold purchases up to the third level
- Dual role system: Users act as both affiliates and network leaders

### Example Scenario:
When a Level 3 user purchases gold:
- Their direct referrer (Level 1) receives 0.7% bonus
- Level 2 referrer receives 0.5% bonus
- Level 3 referrer receives 0.5% bonus

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
