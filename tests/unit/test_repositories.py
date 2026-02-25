"""Unit tests for repositories."""

import pytest
from unittest.mock import Mock, MagicMock
from app.repositories.user import UserRepository
from app.repositories.tenant import TenantRepository
from app.models.user import User
from app.models.tenant import Tenant


@pytest.fixture
def mock_db():
    """Mock database session."""
    return Mock()


class TestUserRepository:
    """Tests for UserRepository."""
    
    def test_get_by_email(self, mock_db):
        """Test getting user by email."""
        repo = UserRepository(User, mock_db)
        mock_user = User(id=1, email="test@example.com")
        
        mock_db.query().filter().first.return_value = mock_user
        
        result = repo.get_by_email("test@example.com")
        
        assert result == mock_user
        mock_db.query.assert_called_once_with(User)
    
    def test_get_by_email_not_found(self, mock_db):
        """Test getting non-existent user by email."""
        repo = UserRepository(User, mock_db)
        mock_db.query().filter().first.return_value = None
        
        result = repo.get_by_email("nonexistent@example.com")
        
        assert result is None
    
    def test_get_by_email_with_tenant(self, mock_db):
        """Test getting user by email with tenant filter."""
        repo = UserRepository(User, mock_db)
        mock_user = User(id=1, email="test@example.com", tenant_id=1)
        
        mock_db.query().filter().filter().first.return_value = mock_user
        
        result = repo.get_by_email("test@example.com", tenant_id=1)
        
        assert result == mock_user


class TestTenantRepository:
    """Tests for TenantRepository."""
    
    def test_get_by_slug(self, mock_db):
        """Test getting tenant by slug."""
        repo = TenantRepository(Tenant, mock_db)
        mock_tenant = Tenant(id=1, slug="test-tenant")
        
        mock_db.query().filter().first.return_value = mock_tenant
        
        result = repo.get_by_slug("test-tenant")
        
        assert result == mock_tenant
        mock_db.query.assert_called_once_with(Tenant)
    
    def test_get_by_slug_not_found(self, mock_db):
        """Test getting non-existent tenant by slug."""
        repo = TenantRepository(Tenant, mock_db)
        mock_db.query().filter().first.return_value = None
        
        result = repo.get_by_slug("nonexistent-tenant")
        
        assert result is None
