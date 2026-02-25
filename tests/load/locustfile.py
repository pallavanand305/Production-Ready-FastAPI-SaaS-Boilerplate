"""Load testing scenarios using Locust."""

from locust import HttpUser, task, between, SequentialTaskSet
import random


class AuthenticationScenario(SequentialTaskSet):
    """Authentication flow scenario."""
    
    @task
    def register(self):
        """Register a new user."""
        email = f"loadtest_{random.randint(1000, 9999)}@example.com"
        self.user.email = email
        
        response = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "LoadTest123!",
                "full_name": "Load Test User",
            },
        )
        
        if response.status_code == 201:
            self.user.access_token = response.json()["access_token"]
    
    @task
    def login(self):
        """Login with credentials."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": getattr(self.user, "email", "test@example.com"),
                "password": "LoadTest123!",
            },
        )
        
        if response.status_code == 200:
            self.user.access_token = response.json()["access_token"]
            self.user.refresh_token = response.json()["refresh_token"]
    
    @task
    def refresh_token(self):
        """Refresh access token."""
        if hasattr(self.user, "refresh_token"):
            self.client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": self.user.refresh_token},
            )


class CRUDOperationsScenario(SequentialTaskSet):
    """CRUD operations scenario."""
    
    def on_start(self):
        """Login before starting CRUD operations."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword123",
            },
        )
        
        if response.status_code == 200:
            self.user.access_token = response.json()["access_token"]
            self.user.headers = {
                "Authorization": f"Bearer {self.user.access_token}"
            }
    
    @task
    def list_users(self):
        """List users with pagination."""
        if hasattr(self.user, "headers"):
            self.client.get(
                "/api/v1/users?skip=0&limit=10",
                headers=self.user.headers,
            )
    
    @task
    def create_user(self):
        """Create a new user."""
        if hasattr(self.user, "headers"):
            email = f"loadtest_{random.randint(1000, 9999)}@example.com"
            response = self.client.post(
                "/api/v1/users",
                json={
                    "email": email,
                    "password": "LoadTest123!",
                    "full_name": "Load Test User",
                },
                headers=self.user.headers,
            )
            
            if response.status_code == 201:
                self.user.created_user_id = response.json()["id"]
    
    @task
    def get_user(self):
        """Get user by ID."""
        if hasattr(self.user, "headers") and hasattr(self.user, "created_user_id"):
            self.client.get(
                f"/api/v1/users/{self.user.created_user_id}",
                headers=self.user.headers,
            )
    
    @task
    def update_user(self):
        """Update user."""
        if hasattr(self.user, "headers") and hasattr(self.user, "created_user_id"):
            self.client.put(
                f"/api/v1/users/{self.user.created_user_id}",
                json={"full_name": "Updated Load Test User"},
                headers=self.user.headers,
            )
    
    @task
    def delete_user(self):
        """Delete user."""
        if hasattr(self.user, "headers") and hasattr(self.user, "created_user_id"):
            self.client.delete(
                f"/api/v1/users/{self.user.created_user_id}",
                headers=self.user.headers,
            )


class RateLimitingScenario(SequentialTaskSet):
    """Rate limiting test scenario."""
    
    @task
    def rapid_requests(self):
        """Make rapid requests to test rate limiting."""
        for _ in range(100):
            response = self.client.get("/api/v1/health")
            
            if response.status_code == 429:
                # Rate limit hit
                retry_after = response.headers.get("Retry-After")
                print(f"Rate limit hit. Retry after: {retry_after} seconds")
                break


class HealthCheckScenario(SequentialTaskSet):
    """Health check scenario."""
    
    @task
    def basic_health(self):
        """Check basic health endpoint."""
        self.client.get("/health")
    
    @task
    def readiness_probe(self):
        """Check readiness probe."""
        self.client.get("/api/v1/health/ready")
    
    @task
    def liveness_probe(self):
        """Check liveness probe."""
        self.client.get("/api/v1/health/live")


class APIUser(HttpUser):
    """Simulated API user."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    tasks = {
        AuthenticationScenario: 2,
        CRUDOperationsScenario: 3,
        RateLimitingScenario: 1,
        HealthCheckScenario: 4,
    }


class AuthenticationUser(HttpUser):
    """User focused on authentication."""
    
    wait_time = between(0.5, 2)
    tasks = [AuthenticationScenario]


class CRUDUser(HttpUser):
    """User focused on CRUD operations."""
    
    wait_time = between(1, 3)
    tasks = [CRUDOperationsScenario]


class HealthCheckUser(HttpUser):
    """User focused on health checks."""
    
    wait_time = between(0.1, 0.5)
    tasks = [HealthCheckScenario]
