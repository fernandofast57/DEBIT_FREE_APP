
# Gold Investment Platform API Documentation

## Authentication Endpoints

### POST /api/v1/auth/login
Login to the platform
- Request: `{ "email": string, "password": string }`
- Response: `{ "token": string, "user": Object }`

### POST /api/v1/auth/register
Register new user
- Request: `{ "email": string, "password": string, "name": string }`
- Response: `{ "message": string, "user_id": number }`

## Transformation Endpoints

### POST /api/v1/transformations/transform
Transform money to gold
- Request: `{ "amount": number, "currency": string }`
- Response: `{ "transaction_id": string, "gold_amount": number }`

### GET /api/v1/transformations/history
Get transformation history
- Response: `{ "transformations": Array<Transformation> }`

## Noble System Endpoints

### GET /api/v1/noble/rank
Get current noble rank
- Response: `{ "rank": string, "benefits": Array<string> }`

### GET /api/v1/noble/bonuses
Get noble system bonuses
- Response: `{ "direct_bonus": number, "network_bonus": number }`

## Transaction Endpoints

### GET /api/v1/transfers/status/:id
Get transfer status
- Parameters: `id: string`
- Response: `{ "status": string, "details": Object }`

## Error Responses
All endpoints may return these status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 500: Internal Server Error
