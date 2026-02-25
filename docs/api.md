# API Documentation

## Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com
```

## API Version

Current version: `v1`

All endpoints are prefixed with `/api/v1`

## Authentication

### JWT Bearer Token

All protected endpoints require a JWT bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Token Expiration

- **Access Token**: 15 minutes
- **Refresh Token**: 7 days

## Endpoints

### Authentication

#### Register User

```http
POST /api/v1/auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe"
}
```

**Response:** `201 Created`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### Login

```http
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### Refresh Token

```http
POST /api/v1/auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### Logout

```http
POST /api/v1/auth/logout
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "message": "Successfully logged out"
}
```

---

### Users

#### List Users

```http
GET /api/v1/users?skip=0&limit=10
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 10, max: 100)

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "email": "user@example.com",
      "full_name": "John Doe",
      "is_active": true,
      "tenant_id": 1,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

#### Get User by ID

```http
GET /api/v1/users/{user_id}
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "tenant_id": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Create User

```http
POST /api/v1/users
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "SecurePassword123!",
  "full_name": "Jane Smith"
}
```

**Response:** `201 Created`
```json
{
  "id": 2,
  "email": "newuser@example.com",
  "full_name": "Jane Smith",
  "is_active": true,
  "tenant_id": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Update User

```http
PUT /api/v1/users/{user_id}
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "full_name": "Jane Doe",
  "is_active": true
}
```

**Response:** `200 OK`
```json
{
  "id": 2,
  "email": "newuser@example.com",
  "full_name": "Jane Doe",
  "is_active": true,
  "tenant_id": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Delete User (Soft Delete)

```http
DELETE /api/v1/users/{user_id}
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "message": "User deleted successfully"
}
```

---

### Tenants

#### List Tenants

```http
GET /api/v1/tenants?skip=0&limit=10
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Permissions Required:** `tenants:read`

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "name": "Acme Corp",
      "slug": "acme-corp",
      "settings": {"tier": "enterprise"},
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

#### Get Tenant by ID

```http
GET /api/v1/tenants/{tenant_id}
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Permissions Required:** `tenants:read`

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Acme Corp",
  "slug": "acme-corp",
  "settings": {"tier": "enterprise"},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Create Tenant (Admin Only)

```http
POST /api/v1/tenants
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Permissions Required:** `tenants:admin`

**Request Body:**
```json
{
  "name": "New Company",
  "slug": "new-company",
  "settings": {"tier": "standard"}
}
```

**Response:** `201 Created`
```json
{
  "id": 2,
  "name": "New Company",
  "slug": "new-company",
  "settings": {"tier": "standard"},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Update Tenant (Admin Only)

```http
PUT /api/v1/tenants/{tenant_id}
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Permissions Required:** `tenants:admin`

**Request Body:**
```json
{
  "name": "Updated Company Name",
  "settings": {"tier": "enterprise"}
}
```

**Response:** `200 OK`
```json
{
  "id": 2,
  "name": "Updated Company Name",
  "slug": "new-company",
  "settings": {"tier": "enterprise"},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

### Tasks

#### Enqueue Task

```http
POST /api/v1/tasks
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "task_type": "send_email",
  "data": {
    "recipient": "user@example.com",
    "subject": "Welcome",
    "body": "Welcome to our platform!"
  }
}
```

**Response:** `202 Accepted`
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Task send_email enqueued successfully"
}
```

#### Get Task Status

```http
GET /api/v1/tasks/{task_id}/status
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "result": {
    "status": "success",
    "recipient": "user@example.com",
    "subject": "Welcome"
  },
  "error": null
}
```

**Task Statuses:**
- `pending`: Task is waiting to be executed
- `running`: Task is currently executing
- `completed`: Task completed successfully
- `failed`: Task failed with an error
- `retrying`: Task is being retried after failure
- `cancelled`: Task was cancelled

---

### Health Checks

#### Basic Health Check

```http
GET /health
```

**Response:** `200 OK`
```json
{
  "status": "healthy"
}
```

#### Readiness Probe

```http
GET /api/v1/health/ready
```

**Response:** `200 OK`
```json
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "redis": "ok"
  }
}
```

#### Liveness Probe

```http
GET /api/v1/health/live
```

**Response:** `200 OK`
```json
{
  "status": "alive"
}
```

---

## Error Responses

All errors follow a consistent format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format",
        "type": "value_error"
      }
    ],
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### Common Error Codes

- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (e.g., duplicate email)
- `413 Request Entity Too Large`: Request body too large
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Rate Limiting

When rate limit is exceeded:

**Response:** `429 Too Many Requests`
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Headers:**
```
Retry-After: 60
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995200
```

---

## Pagination

List endpoints support pagination with `skip` and `limit` parameters:

```http
GET /api/v1/users?skip=20&limit=10
```

**Response includes:**
- `items`: Array of results
- `total`: Total number of items
- `skip`: Number of items skipped
- `limit`: Maximum items returned

---

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

---

## Code Examples

### Python (requests)

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "user@example.com", "password": "password123"}
)
tokens = response.json()

# Use access token
headers = {"Authorization": f"Bearer {tokens['access_token']}"}
response = requests.get(
    "http://localhost:8000/api/v1/users",
    headers=headers
)
users = response.json()
```

### cURL

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Get users
curl -X GET http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer <access_token>"
```

### JavaScript (fetch)

```javascript
// Login
const response = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});
const tokens = await response.json();

// Get users
const usersResponse = await fetch('http://localhost:8000/api/v1/users', {
  headers: {'Authorization': `Bearer ${tokens.access_token}`}
});
const users = await usersResponse.json();
```
