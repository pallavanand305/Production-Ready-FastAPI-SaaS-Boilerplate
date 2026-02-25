# Quick Start Guide

This guide will help you get the FastAPI SaaS boilerplate up and running in minutes.

## Prerequisites

- Python 3.11+
- Docker and Docker Compose (recommended)
- PostgreSQL 14+ (if not using Docker)
- Redis 7.0+ (if not using Docker)

## Option 1: Docker Compose (Recommended)

The easiest way to get started is using Docker Compose:

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd production-ready-fastapi-template

# 2. Start all services
docker-compose -f docker/docker-compose.yml up

# 3. In another terminal, run migrations
docker-compose -f docker/docker-compose.yml exec api alembic upgrade head

# 4. Initialize database with default roles
docker-compose -f docker/docker-compose.yml exec api python scripts/init_db.py
```

The API will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health

## Option 2: Local Development

If you prefer to run services locally:

### 1. Install Dependencies

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install
```

### 2. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and update these values:
# - SECRET_KEY (generate with: openssl rand -hex 32)
# - DATABASE_URL (your PostgreSQL connection string)
# - REDIS_URL (your Redis connection string)
```

### 3. Start PostgreSQL and Redis

```bash
# Using Docker
docker run -d --name postgres -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=fastapi_saas \
  postgres:14-alpine

docker run -d --name redis -p 6379:6379 redis:7-alpine
```

### 4. Run Database Migrations

```bash
# Create initial migration
poetry run alembic revision --autogenerate -m "Initial migration"

# Apply migrations
poetry run alembic upgrade head

# Initialize database with default roles
poetry run python scripts/init_db.py
```

### 5. Start the Application

```bash
# Start API server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start Celery worker (optional)
poetry run celery -A app.worker.celery_app worker --loglevel=info
```

## Testing the API

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "full_name": "John Doe",
    "tenant_slug": "default"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

Save the `access_token` from the response.

### 3. Access Protected Endpoint

```bash
curl -X GET "http://localhost:8000/api/v1/health/ready" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## API Documentation

Once the application is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Health Checks

- **Basic Health**: http://localhost:8000/health
- **Readiness Probe**: http://localhost:8000/api/v1/health/ready
- **Liveness Probe**: http://localhost:8000/api/v1/health/live

## Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_auth.py
```

## Common Issues

### Database Connection Error

If you see database connection errors:
1. Ensure PostgreSQL is running
2. Check DATABASE_URL in .env
3. Verify database exists: `psql -U postgres -c "CREATE DATABASE fastapi_saas;"`

### Redis Connection Error

If you see Redis connection errors:
1. Ensure Redis is running
2. Check REDIS_URL in .env
3. Test connection: `redis-cli ping`

### Migration Errors

If migrations fail:
1. Check database connectivity
2. Ensure all models are imported in alembic/env.py
3. Try: `poetry run alembic downgrade -1` then `poetry run alembic upgrade head`

## Next Steps

1. **Explore the API**: Use the Swagger UI at http://localhost:8000/docs
2. **Read the Documentation**: Check out the docs/ folder
3. **Customize**: Modify models, add endpoints, configure settings
4. **Deploy**: Follow the deployment guide in docs/deployment.md

## Stopping Services

### Docker Compose

```bash
docker-compose -f docker/docker-compose.yml down
```

### Local Development

```bash
# Stop the API server (Ctrl+C)
# Stop Celery worker (Ctrl+C)

# Stop Docker containers
docker stop postgres redis
docker rm postgres redis
```

## Getting Help

- Check the [README.md](README.md) for detailed documentation
- Review [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for current status
- Open an issue on GitHub for bugs or questions

Happy coding! 🚀
