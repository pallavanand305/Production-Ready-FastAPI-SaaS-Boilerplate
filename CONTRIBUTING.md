# Contributing to Production-Ready FastAPI SaaS Boilerplate

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Maintain a professional environment

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Poetry for dependency management
- Git

### Setup Development Environment

```bash
# 1. Fork and clone the repository
git clone https://github.com/yourusername/production-ready-fastapi-template.git
cd production-ready-fastapi-template

# 2. Install dependencies
poetry install

# 3. Install pre-commit hooks
poetry run pre-commit install

# 4. Start services
docker-compose -f docker/docker-compose.yml up -d

# 5. Run migrations
docker-compose -f docker/docker-compose.yml exec api alembic upgrade head
docker-compose -f docker/docker-compose.yml exec api python scripts/init_db.py
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Write clean, readable code
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write docstrings for public functions
- Keep functions focused and small

### 3. Write Tests

```bash
# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app

# Run specific test
poetry run pytest tests/integration/test_auth_api.py
```

### 4. Run Linting

```bash
# Run ruff
poetry run ruff check app

# Run mypy
poetry run mypy app

# Format with black
poetry run black app
```

### 5. Commit Changes

```bash
# Pre-commit hooks will run automatically
git add .
git commit -m "feat: add new feature"
```

### Commit Message Format

Follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: add user profile endpoint
fix: resolve rate limiting bug
docs: update API documentation
test: add integration tests for auth
```

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style Guidelines

### Python Code

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use meaningful variable names
- Add docstrings to all public functions

Example:

```python
def create_user(
    email: str,
    password: str,
    tenant_id: int,
) -> User:
    """
    Create a new user.
    
    Args:
        email: User email address
        password: Plain text password
        tenant_id: Tenant ID
        
    Returns:
        Created user instance
        
    Raises:
        ValueError: If email already exists
    """
    # Implementation
    pass
```

### API Endpoints

- Use RESTful conventions
- Include proper status codes
- Add request/response examples in docstrings
- Implement proper error handling

### Database Models

- Use descriptive field names
- Add comments for complex fields
- Include relationships
- Use soft deletes where appropriate

### Tests

- Write descriptive test names
- Test happy path and error cases
- Use fixtures for common setup
- Aim for 80%+ code coverage

## Pull Request Process

1. **Update Documentation**: Update README or docs if needed
2. **Add Tests**: Ensure new code has test coverage
3. **Run Tests**: All tests must pass
4. **Update Changelog**: Add entry to CHANGELOG.md
5. **Request Review**: Tag maintainers for review

### Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts
- [ ] CI pipeline passing

## Testing Guidelines

### Unit Tests

- Test individual functions/methods
- Mock external dependencies
- Fast execution
- Located in `tests/unit/`

### Integration Tests

- Test API endpoints
- Use test database
- Test authentication flow
- Located in `tests/integration/`

### Test Fixtures

Use pytest fixtures for common setup:

```python
@pytest.fixture
def test_user(db_session):
    """Create test user."""
    user = User(email="test@example.com", ...)
    db_session.add(user)
    db_session.commit()
    return user
```

## Documentation

### Code Documentation

- Add docstrings to all public functions
- Include type hints
- Document parameters and return values
- Add usage examples for complex functions

### API Documentation

- FastAPI automatically generates OpenAPI docs
- Add descriptions to endpoints
- Include request/response examples
- Document error responses

### README Updates

Update README.md when:
- Adding new features
- Changing configuration
- Updating dependencies
- Modifying setup process

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create git tag: `git tag v1.0.0`
4. Push tag: `git push origin v1.0.0`
5. GitHub Actions will build and publish

## Questions?

- Open an issue for bugs
- Start a discussion for questions
- Check existing issues first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
