"""Unit tests for CacheService."""

import pytest
from unittest.mock import Mock, patch
from app.services.cache import CacheService


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    return Mock()


@pytest.fixture
def cache_service(mock_redis):
    """Create CacheService instance with mock Redis."""
    with patch('app.services.cache.redis.Redis', return_value=mock_redis):
        service = CacheService()
        service.redis = mock_redis
        return service


class TestCacheGet:
    """Tests for cache get operation."""
    
    def test_get_existing_key(self, cache_service, mock_redis):
        """Test getting existing cache key."""
        mock_redis.get.return_value = b'"test_value"'
        
        result = cache_service.get("test_key")
        
        assert result == "test_value"
        mock_redis.get.assert_called_once_with("test_key")
    
    def test_get_nonexistent_key(self, cache_service, mock_redis):
        """Test getting non-existent cache key."""
        mock_redis.get.return_value = None
        
        result = cache_service.get("nonexistent_key")
        
        assert result is None
    
    def test_get_with_redis_error(self, cache_service, mock_redis):
        """Test graceful degradation when Redis fails."""
        mock_redis.get.side_effect = Exception("Redis connection error")
        
        result = cache_service.get("test_key")
        
        assert result is None  # Graceful degradation


class TestCacheSet:
    """Tests for cache set operation."""
    
    def test_set_with_ttl(self, cache_service, mock_redis):
        """Test setting cache key with TTL."""
        cache_service.set("test_key", "test_value", ttl=300)
        
        mock_redis.setex.assert_called_once()
        args = mock_redis.setex.call_args[0]
        assert args[0] == "test_key"
        assert args[1] == 300
    
    def test_set_without_ttl(self, cache_service, mock_redis):
        """Test setting cache key without TTL."""
        cache_service.set("test_key", "test_value")
        
        mock_redis.set.assert_called_once()
    
    def test_set_with_redis_error(self, cache_service, mock_redis):
        """Test graceful degradation when Redis fails."""
        mock_redis.setex.side_effect = Exception("Redis connection error")
        
        # Should not raise exception
        cache_service.set("test_key", "test_value", ttl=300)


class TestCacheDelete:
    """Tests for cache delete operation."""
    
    def test_delete_existing_key(self, cache_service, mock_redis):
        """Test deleting existing cache key."""
        mock_redis.delete.return_value = 1
        
        result = cache_service.delete("test_key")
        
        assert result is True
        mock_redis.delete.assert_called_once_with("test_key")
    
    def test_delete_nonexistent_key(self, cache_service, mock_redis):
        """Test deleting non-existent cache key."""
        mock_redis.delete.return_value = 0
        
        result = cache_service.delete("nonexistent_key")
        
        assert result is False


class TestCacheDeletePattern:
    """Tests for cache delete pattern operation."""
    
    def test_delete_pattern(self, cache_service, mock_redis):
        """Test deleting keys by pattern."""
        mock_redis.scan_iter.return_value = [b"key1", b"key2", b"key3"]
        
        cache_service.delete_pattern("test:*")
        
        mock_redis.scan_iter.assert_called_once_with(match="test:*", count=100)
        assert mock_redis.delete.call_count == 3
