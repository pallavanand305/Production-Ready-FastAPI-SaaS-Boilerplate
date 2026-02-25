"""Unit tests for AuthService."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from app.services.auth import AuthService
from app.models.user import User
from app.models.tenant import Tenant
from app.core.security import hash_password


@pytest.fixture
def mock_db():
    """Mock database session."""
    return Mock()


@pytest.fixture
def mock_cache():
    """Mock cache service."""
    return Mock()


@pytest.fixture
def auth_service(mock_db, mock_cache):
    """Create AuthService instance with mocks."""
    return AuthService(db=mock_db, cache=mock_cache)


@pytest.fixture
def test_user():
    """Create test user."""
    tenant = Tenant(id=1, name="Test Tenant", slug="test-tenant")
    user = User(
        id=1,
        email="test@example.com",
        hashed_password=hash_password("password123"),
        full_name="Test User",
        tenant_id=1,
        tenant=tenant,
        is_active=True,
        failed_login_attempts=0,
    )
    return user


class TestAuthenticateUser:
    """Tests for authenticate_user method."""
    
    def test_authenticate_user_success(self, auth_service, mock_db, test_user):
        """Test successful user authentication."""
        # Mock database query
        mock_db.query().filter().first.return_value = test_user
        
        # Authenticate
        result = auth_service.authenticate_user("test@example.com", "password123")
        
        assert result is not None
        assert result.email == "test@example.com"
        assert result.failed_login_attempts == 0
    
    def test_authenticate_user_invalid_password(self, auth_service, mock_db, test_user):
        """Test authentication with invalid password."""
        mock_db.query().filter().first.return_value = test_user
        
        result = auth_service.authenticate_user("test@example.com", "wrongpassword")
        
        assert result is None
        # Verify failed attempt was incremented
        mock_db.commit.assert_called_once()
    
    def test_authenticate_user_not_found(self, auth_service, mock_db):
        """Test authentication with non-existent user."""
        mock_db.query().filter().first.return_value = None
        
        result = auth_service.authenticate_user("nonexistent@example.com", "password123")
        
        assert result is None
    
    def test_authenticate_user_inactive(self, auth_service, mock_db, test_user):
        """Test authentication with inactive user."""
        test_user.is_active = False
        mock_db.query().filter().first.return_value = test_user
        
        result = auth_service.authenticate_user("test@example.com", "password123")
        
        assert result is None
    
    def test_authenticate_user_locked(self, auth_service, mock_db, test_user):
        """Test authentication with locked account."""
        test_user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        mock_db.query().filter().first.return_value = test_user
        
        result = auth_service.authenticate_user("test@example.com", "password123")
        
        assert result is None


class TestCreateTokenPair:
    """Tests for create_token_pair method."""
    
    def test_create_token_pair_success(self, auth_service, mock_db, test_user):
        """Test successful token pair creation."""
        tokens = auth_service.create_token_pair(test_user)
        
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
        
        # Verify refresh token was saved
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


class TestCheckPermission:
    """Tests for check_permission method."""
    
    def test_check_permission_with_permission(self, auth_service, test_user):
        """Test permission check when user has permission."""
        # Mock user permissions
        from app.models.role import Permission
        permission = Permission(name="users:read", description="Read users")
        test_user.get_permissions = Mock(return_value=[permission])
        
        result = auth_service.check_permission(test_user, "users:read")
        
        assert result is True
    
    def test_check_permission_without_permission(self, auth_service, test_user):
        """Test permission check when user lacks permission."""
        test_user.get_permissions = Mock(return_value=[])
        
        result = auth_service.check_permission(test_user, "users:delete")
        
        assert result is False
