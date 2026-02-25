# Production-Ready FastAPI SaaS Boilerplate

A drop-in backend starter for building production-ready SaaS applications with FastAPI. This boilerplate demonstrates industry-standard practices for backend development, DevOps, and cloud deployment.

## 🎯 Features

- **Multi-Tenant Architecture**: Complete data isolation with tenant-scoped queries
- **JWT Authentication**: Secure authentication with RBAC and refresh token rotation
- **Redis Caching**: Performance optimization with cache-aside pattern
- **Celery Workers**: Asynchronous task processing with retry logic
- **API Rate Limiting**: Token bucket algorithm with per-user and per-IP limits
- **Structured Logging**: JSON logging with request tracing
- **Health Checks**: Kubernetes-ready liveness and readiness probes
- **Docker Support**: Multi-stage builds with docker-compose for local development
- **CI/CD Pipeline**: GitHub Actions with automated testing and deployment
- **Infrastructure as Code**: Terraform modules for AWS (VPC, RDS, ElastiCache, ECS, ALB)
- **Comprehensive Testing**: Unit, integration, and property-based tests with 80%+ coverage
- **Security Best Practices**: HTTPS, security headers, input sanitization, SQL injection prevention

## 🧰 Tech Stack

- **Framework**: FastAPI 0.109+
- **Database**: PostgreSQL 14+ with SQLAlchemy 2.0+
- **Cache**: Redis 7.0+
- **Task Queue**: Celery 5.3+ with Redis broker
- **Container**: Docker with Docker Compose
- **Infrastructure**: Terraform for AWS deployment
- **CI/CD**: GitHub Actions
- **Testing**: pytest, Hypothesis, Locust

## 📂 Project Structure

```
production-ready-fastapi-template/
├── app/
│   ├── api/                    # API endpoints
│   │   ├── deps.py            # Dependencies (auth, db session)
│   │   └── v1/
│   │       ├── api.py         # API router aggregation
│   │       └── endpoints/     # Endpoint modules
│   ├── core/                  # Core configuration
│   │   ├── config.py          # Settings management
│   │   ├── logging.py         # Structured logging
│   │   └── security.py        # Security utilities
│   ├── db/                    # Database layer
│   │   └── session.py         # Session management
│   ├── models/                # SQLAlchemy models
│   │   ├── base.py           # Base model with timestamps
│   │   ├── tenant.py         # Tenant model
│   │   ├── user.py           # User model
│   │   ├── role.py           # Role & Permission models
│   │   └── refresh_token.py  # RefreshToken model
│   ├── repositories/          # Repository pattern
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic
│   ├── middleware/            # Custom middleware
│   ├── worker/                # Celery tasks
│   └── main.py               # Application entry point
├── alembic/                   # Database migrations
├── tests/                     # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   ├── property/             # Property-based tests
│   └── load/                 # Load tests
├── terraform/                 # Infrastructure as code
│   ├── modules/              # Terraform modules
│   └── environments/         # Environment configs
├── docker/                    # Docker configurations
│   ├── Dockerfile            # Production image
│   ├── Dockerfile.dev        # Development image
│   └── docker-compose.yml    # Local development
├── .github/workflows/         # CI/CD pipelines
├── docs/                      # Documentation
├── scripts/                   # Utility scripts
├── .env.example              # Environment variables template
├── pyproject.toml            # Poetry dependencies
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 14+ (or use Docker Compose)
- Redis 7.0+ (or use Docker Compose)

### Local Development Setup

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/production-ready-fastapi-template.git
cd production-ready-fastapi-template
```

2. **Install dependencies**

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install
```

3. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env and set your configuration
```

4. **Start services with Docker Compose**

```bash
docker-compose -f docker/docker-compose.yml up -d
```

5. **Run database migrations**

```bash
poetry run alembic upgrade head
```

6. **Start the development server**

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. **Access the application**

- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative API Documentation: http://localhost:8000/redoc

### Using Docker Compose (Recommended for Development)

```bash
# Start all services (API, Worker, PostgreSQL, Redis)
docker-compose -f docker/docker-compose.yml up

# Run in detached mode
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop services
docker-compose -f docker/docker-compose.yml down
```

## 🧪 Testing

### Run all tests

```bash
poetry run pytest
```

### Run with coverage

```bash
poetry run pytest --cov=app --cov-report=html --cov-report=term-missing
```

### Run specific test types

```bash
# Unit tests only
poetry run pytest tests/unit/

# Integration tests only
poetry run pytest tests/integration/

# Property-based tests only
poetry run pytest tests/property/
```

### Load testing

```bash
# Install locust
poetry add locust --group dev

# Run load tests
poetry run locust -f tests/load/locustfile.py --host=http://localhost:8000
```

## 🔧 Configuration

All configuration is managed through environment variables. See `.env.example` for all available options.

### Key Configuration Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | Required |
| `SECRET_KEY` | JWT secret key (min 32 chars) | Required |
| `ENVIRONMENT` | Environment name (development/staging/production) | development |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | INFO |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | localhost:3000 |

## 🏗️ Database Migrations

### Create a new migration

```bash
poetry run alembic revision --autogenerate -m "description of changes"
```

### Apply migrations

```bash
# Upgrade to latest
poetry run alembic upgrade head

# Upgrade to specific revision
poetry run alembic upgrade <revision_id>
```

### Rollback migrations

```bash
# Downgrade one revision
poetry run alembic downgrade -1

# Downgrade to specific revision
poetry run alembic downgrade <revision_id>
```

## 🔐 Security

This boilerplate implements security best practices:

- **Password Hashing**: Bcrypt with 12+ rounds
- **JWT Tokens**: Secure token generation with expiration
- **Refresh Token Rotation**: Enhanced security for long-lived sessions
- **Account Lockout**: Protection against brute-force attacks
- **Rate Limiting**: Prevent API abuse
- **Input Validation**: Pydantic models for request validation
- **SQL Injection Prevention**: Parameterized queries via SQLAlchemy ORM
- **HTTPS Enforcement**: Production-only HTTPS
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
- **Sensitive Data Sanitization**: Automatic redaction in logs

## 📊 Monitoring and Logging

### Structured Logging

All logs are output in JSON format for easy parsing and analysis:

```json
{
  "timestamp": "2024-01-01T00:00:00.000Z",
  "level": "INFO",
  "message": "Request completed",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "1",
  "user_id": "42",
  "method": "GET",
  "path": "/api/v1/users",
  "status_code": 200,
  "duration_ms": 45
}
```

### Health Checks

- `/health` - Basic health check
- `/health/ready` - Readiness probe (checks database and Redis)
- `/health/live` - Liveness probe

## 🚢 Deployment

### AWS Deployment with Terraform

1. **Configure AWS credentials**

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
```

2. **Initialize Terraform**

```bash
cd terraform
terraform init
```

3. **Plan deployment**

```bash
terraform plan -var-file=environments/prod.tfvars
```

4. **Apply infrastructure**

```bash
terraform apply -var-file=environments/prod.tfvars
```

### Docker Deployment

Build and push Docker image:

```bash
# Build production image
docker build -t fastapi-saas:latest -f docker/Dockerfile .

# Tag for registry
docker tag fastapi-saas:latest your-registry/fastapi-saas:latest

# Push to registry
docker push your-registry/fastapi-saas:latest
```

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`poetry run pytest`)
5. Run linting (`poetry run ruff check .`)
6. Run type checking (`poetry run mypy app`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- SQLAlchemy for the powerful ORM
- Celery for distributed task processing
- The Python community for amazing tools and libraries

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for the developer community**
