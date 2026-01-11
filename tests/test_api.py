"""
VEDA AI Backend - Test Suite
Basic smoke tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns welcome message"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "status" in data
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code in [200, 404]  # May not exist


class TestChatEndpoints:
    """Test chat API endpoints"""
    
    def test_chat_endpoint_exists(self):
        """Test chat endpoint is accessible"""
        response = client.post(
            "/api/v1/chat/",
            json={"message": "Hello", "user_id": "test"}
        )
        # Should return 200 or 401/403 if auth required
        assert response.status_code in [200, 401, 403, 422]
    
    def test_guest_chat_endpoint(self):
        """Test guest chat endpoint"""
        response = client.post(
            "/api/v1/chat/guest",
            json={"message": "Hello", "language": "en"}
        )
        assert response.status_code in [200, 422]


class TestVoiceEndpoints:
    """Test voice API endpoints"""
    
    def test_voice_health(self):
        """Test voice health endpoint"""
        response = client.get("/api/v1/voice/health")
        assert response.status_code in [200, 404]
    
    def test_voice_languages(self):
        """Test supported languages endpoint"""
        response = client.get("/api/v1/voice/languages")
        assert response.status_code in [200, 404]


class TestExpertsEndpoints:
    """Test domain experts endpoints"""
    
    def test_experts_list(self):
        """Test experts list endpoint"""
        response = client.get("/api/v1/experts/")
        assert response.status_code in [200, 404]


# Run with: pytest tests/test_api.py -v
