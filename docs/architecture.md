# Architecture Documentation

## System Overview

This FastAPI SaaS boilerplate implements a production-ready multi-tenant architecture with complete data isolation, JWT authentication, Redis caching, and Celery background processing.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│                    (Web/Mobile/API Clients)                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Load Balancer (ALB)                     │
│                    (HTTPS, Health Checks)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Middleware Stack                         │  │
│  │  • HTTPS Redirect                                     │  │
│  │  • Security Headers                                   │  │
│  │  • Request Size Limiting                              │  │
│  │  • Rate Limiting (Redis)                              │  │
│  │  • Tenant Context Extraction                          │  │
│  │  • Request Logging                                    │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Endpoints                            │  │
│  │  • Authentication (JWT)                               │  │
│  │  • Users CRUD                                         │  │
│  │  • Tenants CRUD                                       │  │
│  │  • Tasks (Background Jobs)                            │  │
│  │  • Health Checks                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Business Logic Layer                     │  │
│  │  • AuthService (JWT, RBAC)                            │  │
│  │  • UserService (CRUD, Caching)                        │  │
│  │  • CacheService (Redis)                               │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Data Access Layer                        │  │
│  │  • Repository Pattern                                 │  │
│  │  • Tenant Filtering                                   │  │
│  │  • SQLAlchemy ORM                                     │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────┬──────────────────────────┬─────────────────────┘
            │                          │
            ▼                          ▼
┌───────────────────────┐  ┌──────────────────────────┐
│   PostgreSQL DB       │  │      Redis Cache         │
│  • Multi-tenant data  │  │  • Session storage       │
│  • Connection pooling │  │  • Rate limiting         │
│  • Soft deletes       │  │  • Cache layer           │
└───────────────────────┘  └──────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Celery Workers                            │
│  • Background task processing                                │
│  • Email sending                                             │
│  • Data processing                                           │
│  • Scheduled tasks (token cleanup)                           │
└─────────────────────────────────────────────────────────────┘
```

## Multi-Tenant Architecture

### Tenant Isolation Strategy

1. **Database Level**: Each record has a `tenant_id` foreign key
2. **Repository Level**: All queries automatically filter by tenant
3. **Middleware Level**: Tenant context extracted from JWT token
4. **Cache Level**: Cache keys namespaced by tenant ID

### Tenant Context Flow

```
Request → JWT Token → Extract tenant_id → Set in request.state → 
Repository filters by tenant_id → Response
```

## Authentication & Authorization

### JWT Token Flow

```
1. User Login
   ↓
2. Validate Credentials
   ↓
3. Generate Access Token (15 min) + Refresh Token (7 days)
   ↓
4. Store Refresh Token in DB
   ↓
5. Return Tokens to Client
   ↓
6. Client uses Access Token for API calls
   ↓
7. When Access Token expires, use Refresh Token
   ↓
8. Generate new Access Token + Rotate Refresh Token
```

### RBAC (Role-Based Access Control)

- **Roles**: Admin, User, Guest
- **Permissions**: Resource:Action (e.g., users:read, users:write)
- **Assignment**: Users → Roles → Permissions
- **Enforcement**: Dependency injection in endpoints

## Caching Strategy

### Cache Layers

1. **Application Cache**: Redis for frequently accessed data
2. **Database Cache**: SQLAlchemy query cache
3. **HTTP Cache**: Response caching headers

### Cache Invalidation

- **Time-based**: TTL on all cache entries
- **Event-based**: Invalidate on mutations (create, update, delete)
- **Pattern-based**: Delete by key pattern (e.g., `tenant:123:*`)

### Graceful Degradation

If Redis is unavailable:
- Application continues to function
- Queries hit database directly
- Performance degrades but no errors

## Background Task Processing

### Celery Architecture

```
FastAPI → Enqueue Task → Redis (Broker) → Celery Worker → 
Process Task → Store Result → Redis (Backend)
```

### Task Types

1. **Async Tasks**: Email sending, data processing
2. **Scheduled Tasks**: Token cleanup, report generation
3. **Priority Tasks**: High-priority operations

### Retry Strategy

- **Exponential Backoff**: 2^retry_count seconds
- **Max Retries**: 3 attempts
- **Jitter**: Random delay to prevent thundering herd

## Security Architecture

### Defense in Depth

1. **Network Layer**: HTTPS only, security headers
2. **Application Layer**: Input validation, rate limiting
3. **Authentication Layer**: JWT tokens, refresh rotation
4. **Authorization Layer**: RBAC, permission checks
5. **Data Layer**: SQL injection prevention, soft deletes

### Security Headers

- `Strict-Transport-Security`: Force HTTPS
- `X-Content-Type-Options`: Prevent MIME sniffing
- `X-Frame-Options`: Prevent clickjacking
- `Content-Security-Policy`: XSS protection
- `X-XSS-Protection`: Browser XSS filter

## Database Schema

### Core Tables

```
tenants
├── id (PK)
├── name
├── slug (unique)
├── settings (JSONB)
├── created_at
└── updated_at

users
├── id (PK)
├── tenant_id (FK → tenants)
├── email (unique per tenant)
├── hashed_password
├── full_name
├── is_active
├── failed_login_attempts
├── locked_until
├── created_at
└── updated_at

roles
├── id (PK)
├── name
└── description

permissions
├── id (PK)
├── resource
└── action

user_roles (many-to-many)
├── user_id (FK → users)
└── role_id (FK → roles)

role_permissions (many-to-many)
├── role_id (FK → roles)
└── permission_id (FK → permissions)

refresh_tokens
├── id (PK)
├── user_id (FK → users)
├── token (unique)
├── expires_at
├── revoked
└── created_at
```

## Deployment Architecture

### Container Strategy

```
Docker Image → Container Registry → ECS/Kubernetes → 
Load Balancer → Auto Scaling
```

### Environment Separation

- **Development**: Local Docker Compose
- **Staging**: AWS ECS with reduced resources
- **Production**: AWS ECS with auto-scaling

## Monitoring & Observability

### Logging

- **Structured JSON Logs**: Machine-readable format
- **Request ID**: Trace requests across services
- **Sensitive Data Sanitization**: Remove passwords, tokens

### Health Checks

- **Liveness**: Is the application running?
- **Readiness**: Can it handle requests?
- **Dependency Checks**: Database, Redis connectivity

### Metrics (Future)

- Request rate, latency, error rate
- Database connection pool usage
- Cache hit/miss ratio
- Background task queue length

## Scalability Considerations

### Horizontal Scaling

- **Stateless API**: Can run multiple instances
- **Shared State**: Redis for sessions, rate limiting
- **Database**: Connection pooling, read replicas

### Vertical Scaling

- **CPU**: Background task processing
- **Memory**: Cache size, connection pools
- **Storage**: Database size, log retention

## Performance Optimization

### Database

- **Indexes**: On foreign keys, frequently queried columns
- **Connection Pooling**: Reuse connections
- **Query Optimization**: N+1 prevention, eager loading

### Caching

- **Cache Warming**: Pre-populate frequently accessed data
- **Cache Aside**: Load on miss, cache on hit
- **TTL Strategy**: Balance freshness vs performance

### API

- **Pagination**: Limit result sets
- **Field Selection**: Return only requested fields
- **Compression**: Gzip responses

## Technology Stack

- **Framework**: FastAPI 0.109+
- **Database**: PostgreSQL 14+
- **Cache**: Redis 7+
- **Task Queue**: Celery 5.3+
- **ORM**: SQLAlchemy 2.0+
- **Migration**: Alembic 1.13+
- **Validation**: Pydantic 2.5+
- **Authentication**: python-jose, passlib
- **Testing**: Pytest, Locust
- **CI/CD**: GitHub Actions
- **Containerization**: Docker, Docker Compose

## Design Patterns

1. **Repository Pattern**: Data access abstraction
2. **Service Layer**: Business logic separation
3. **Dependency Injection**: Loose coupling
4. **Circuit Breaker**: Fault tolerance
5. **Middleware Chain**: Request/response processing
6. **Factory Pattern**: Object creation
7. **Strategy Pattern**: Algorithm selection

## Best Practices Implemented

- ✅ Type hints throughout
- ✅ Comprehensive docstrings
- ✅ Error handling with custom exceptions
- ✅ Input validation with Pydantic
- ✅ SQL injection prevention (ORM)
- ✅ XSS prevention (output encoding)
- ✅ CSRF protection (state-changing operations)
- ✅ Rate limiting (prevent abuse)
- ✅ Logging (observability)
- ✅ Testing (quality assurance)
- ✅ Documentation (maintainability)
