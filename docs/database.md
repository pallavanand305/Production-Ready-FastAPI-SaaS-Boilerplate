# Database Documentation

## Overview

This application uses PostgreSQL as the primary database with SQLAlchemy 2.0 as the ORM and Alembic for migrations.

## Connection Configuration

Database connection is configured via environment variables:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
```

## Schema Overview

### Core Tables

#### tenants
Stores tenant (organization) information for multi-tenancy.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Unique identifier |
| name | String(255) | NOT NULL | Tenant name |
| slug | String(100) | UNIQUE, NOT NULL | URL-friendly identifier |
| settings | JSONB | | Tenant-specific settings |
| created_at | DateTime | NOT NULL | Creation timestamp |
| updated_at | DateTime | NOT NULL | Last update timestamp |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete flag |
| deleted_at | DateTime | NULLABLE | Deletion timestamp |

**Indexes:**
- `ix_tenants_slug` on `slug`
- `ix_tenants_is_deleted` on `is_deleted`

#### users
Stores user account information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Unique identifier |
| tenant_id | Integer | FK(tenants.id), NOT NULL | Associated tenant |
| email | String(255) | NOT NULL | User email |
| hashed_password | String(255) | NOT NULL | Bcrypt hashed password |
| full_name | String(255) | | User's full name |
| is_active | Boolean | DEFAULT TRUE | Account active status |
| failed_login_attempts | Integer | DEFAULT 0 | Failed login counter |
| locked_until | DateTime | NULLABLE | Account lock expiration |
| created_at | DateTime | NOT NULL | Creation timestamp |
| updated_at | DateTime | NOT NULL | Last update timestamp |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete flag |
| deleted_at | DateTime | NULLABLE | Deletion timestamp |

**Indexes:**
- `ix_users_email` on `email`
- `ix_users_tenant_id` on `tenant_id`
- `ix_users_is_deleted` on `is_deleted`

**Unique Constraints:**
- `uq_users_email_tenant` on `(email, tenant_id)` - Email unique per tenant

#### roles
Stores role definitions for RBAC.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Unique identifier |
| name | String(50) | UNIQUE, NOT NULL | Role name |
| description | String(255) | | Role description |
| created_at | DateTime | NOT NULL | Creation timestamp |
| updated_at | DateTime | NOT NULL | Last update timestamp |

**Default Roles:**
- `admin`: Full system access
- `user`: Standard user access
- `guest`: Limited read-only access

#### permissions
Stores permission definitions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Unique identifier |
| resource | String(50) | NOT NULL | Resource name (e.g., "users") |
| action | String(50) | NOT NULL | Action name (e.g., "read") |
| created_at | DateTime | NOT NULL | Creation timestamp |
| updated_at | DateTime | NOT NULL | Last update timestamp |

**Unique Constraints:**
- `uq_permissions_resource_action` on `(resource, action)`

**Permission Format:** `resource:action` (e.g., `users:read`, `tenants:admin`)

#### user_roles
Many-to-many relationship between users and roles.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | Integer | FK(users.id), PK | User identifier |
| role_id | Integer | FK(roles.id), PK | Role identifier |

#### role_permissions
Many-to-many relationship between roles and permissions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| role_id | Integer | FK(roles.id), PK | Role identifier |
| permission_id | Integer | FK(permissions.id), PK | Permission identifier |

#### refresh_tokens
Stores JWT refresh tokens for token rotation.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Unique identifier |
| user_id | Integer | FK(users.id), NOT NULL | Associated user |
| token | String(500) | UNIQUE, NOT NULL | Refresh token value |
| expires_at | DateTime | NOT NULL | Token expiration |
| revoked | Boolean | DEFAULT FALSE | Revocation status |
| created_at | DateTime | NOT NULL | Creation timestamp |

**Indexes:**
- `ix_refresh_tokens_token` on `token`
- `ix_refresh_tokens_user_id` on `user_id`

## Relationships

```
tenants (1) ──< (N) users
users (N) ──< (N) roles
roles (N) ──< (N) permissions
users (1) ──< (N) refresh_tokens
```

## Migrations

### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create empty migration
alembic revision -m "Description"
```

### Running Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade <revision_id>

# Downgrade one revision
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history
```

### Migration Best Practices

1. **Always review auto-generated migrations** before applying
2. **Test migrations** on development database first
3. **Include both upgrade and downgrade** operations
4. **Backup database** before running migrations in production
5. **Use transactions** for data migrations

## Soft Deletes

All models inherit soft delete functionality:

- `is_deleted`: Boolean flag
- `deleted_at`: Timestamp of deletion

**Querying:**
```python
# Exclude soft-deleted records (default)
users = db.query(User).filter(User.is_deleted == False).all()

# Include soft-deleted records
all_users = db.query(User).all()
```

## Connection Pooling

SQLAlchemy connection pool configuration:

- **Pool Size**: 20 connections
- **Max Overflow**: 10 additional connections
- **Pool Recycle**: 3600 seconds (1 hour)
- **Pool Pre-ping**: Enabled (checks connection before use)

## Query Optimization

### Indexes

All foreign keys and frequently queried columns have indexes.

### N+1 Prevention

Use `joinedload` or `selectinload` for relationships:

```python
# Bad - N+1 queries
users = db.query(User).all()
for user in users:
    print(user.tenant.name)  # Separate query for each user

# Good - Single query with join
from sqlalchemy.orm import joinedload
users = db.query(User).options(joinedload(User.tenant)).all()
```

### Pagination

Always paginate large result sets:

```python
users = db.query(User).offset(skip).limit(limit).all()
```

## Backup & Recovery

### Backup

```bash
# Full database backup
pg_dump -U username -d dbname > backup.sql

# Compressed backup
pg_dump -U username -d dbname | gzip > backup.sql.gz

# Schema only
pg_dump -U username -d dbname --schema-only > schema.sql
```

### Restore

```bash
# Restore from backup
psql -U username -d dbname < backup.sql

# Restore compressed backup
gunzip -c backup.sql.gz | psql -U username -d dbname
```

## Monitoring

### Connection Pool Stats

```python
from app.db.session import engine

pool = engine.pool
print(f"Pool size: {pool.size()}")
print(f"Checked out: {pool.checkedout()}")
print(f"Overflow: {pool.overflow()}")
```

### Slow Query Logging

Enable in PostgreSQL configuration:

```
log_min_duration_statement = 1000  # Log queries > 1 second
```

## Security

### SQL Injection Prevention

- **Use ORM**: SQLAlchemy prevents SQL injection
- **Parameterized queries**: Always use bound parameters
- **Never concatenate** user input into SQL

### Password Storage

- **Hashing**: Bcrypt with 12+ rounds
- **Never store** plain text passwords
- **Salt**: Automatically handled by bcrypt

### Connection Security

- **SSL/TLS**: Enable for production
- **Least privilege**: Database user has minimal permissions
- **Connection limits**: Prevent resource exhaustion

## Troubleshooting

### Connection Issues

```python
# Test database connection
from app.db.session import SessionLocal

try:
    db = SessionLocal()
    db.execute("SELECT 1")
    print("Database connection successful")
except Exception as e:
    print(f"Database connection failed: {e}")
finally:
    db.close()
```

### Migration Conflicts

```bash
# Show current state
alembic current

# Show pending migrations
alembic heads

# Resolve conflicts by merging branches
alembic merge <rev1> <rev2> -m "Merge migrations"
```

### Lock Timeouts

If experiencing lock timeouts:

1. Check for long-running transactions
2. Reduce transaction scope
3. Use `SELECT FOR UPDATE NOWAIT` for explicit locking
4. Increase `lock_timeout` in PostgreSQL

## Performance Tips

1. **Use indexes** on foreign keys and frequently queried columns
2. **Limit result sets** with pagination
3. **Use connection pooling** to reuse connections
4. **Enable query caching** for read-heavy workloads
5. **Monitor slow queries** and optimize
6. **Use read replicas** for scaling reads
7. **Partition large tables** if needed
8. **Regular VACUUM** and ANALYZE operations
