"""Integration tests for authentication API."""

import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test basic health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_register_user(client: TestClient, test_tenant):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "SecurePassword123!",
            "full_name": "New User",
            "tenant_slug": test_tenant.slug,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_success(client: TestClient, test_user):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_invalid_credentials(client: TestClient, test_user):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


def test_protected_endpoint_without_auth(client: TestClient):
    """Test accessing protected endpoint without authentication."""
    response = client.get("/api/v1/users")
    assert response.status_code == 403


def test_protected_endpoint_with_auth(client: TestClient, auth_headers):
    """Test accessing protected endpoint with authentication."""
    response = client.get("/api/v1/users", headers=auth_headers)
    assert response.status_code == 200
