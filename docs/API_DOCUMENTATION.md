
# Gold Investment Platform API Documentation

## Core Endpoints

### Authentication
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/verify-2fa`

### Transformations
- `POST /api/v1/transformations/transform`
  - Weekly gold transformation
  - Requires: amount, user_id
  - Returns: transformation details

### Noble System
- `GET /api/v1/noble/rank`
  - Get current noble rank
- `GET /api/v1/noble/bonuses`
  - Get bonus distribution history

### Accounting
- `GET /api/v1/accounting/balance`
  - Get current gold and money balance
- `GET /api/v1/accounting/transactions`
  - Get transaction history

## Response Formats
All responses follow the format:
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
