"""Integration tests for API endpoints."""

import pytest
import io
from fastapi.testclient import TestClient
from PIL import Image
import numpy as np

from main import app
from app.core.config import get_settings


class TestHealthEndpoint:
    """Test cases for health check endpoint."""
    
    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)
    
    def test_health_check_success(self):
        """Test successful health check."""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "models_loaded" in data
        assert "timestamp" in data
        
        assert data["status"] in ["healthy", "unhealthy"]
        assert isinstance(data["models_loaded"], bool)
        assert isinstance(data["version"], str)
        assert isinstance(data["timestamp"], str)


class TestAnalysisEndpoints:
    """Test cases for analysis endpoints."""
    
    def setup_method(self):
        """Setup test client and sample image."""
        self.client = TestClient(app)
        
        # Create a sample image for testing
        img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        self.sample_image = Image.fromarray(img_array)
        
        # Convert image to bytes
        self.image_bytes = io.BytesIO()
        self.sample_image.save(self.image_bytes, format='JPEG')
        self.image_bytes.seek(0)
    
    def test_xray_analysis_success(self):
        """Test successful X-ray analysis."""
        files = {"file": ("test_xray.jpg", self.image_bytes, "image/jpeg")}
        
        response = self.client.post("/analyze/xray", files=files)
        
        assert response.status_code == 200
        
        data = response.json()
        assert "request_id" in data
        assert "model_name" in data
        assert "status" in data
        assert "inference_time" in data
        assert "device" in data
        assert "authenticity" in data
        assert "arthritis" in data
        
        # Check structure of authenticity results
        auth = data["authenticity"]
        assert "is_real" in auth
        assert "confidence" in auth
        assert "raw_probability" in auth
        assert isinstance(auth["is_real"], bool)
        assert 0 <= auth["confidence"] <= 1
        assert 0 <= auth["raw_probability"] <= 1
        
        # Check structure of arthritis results
        arthritis = data["arthritis"]
        assert "probabilities" in arthritis
        assert len(arthritis["probabilities"]) == 4
        
        # Check metadata
        assert data["model_name"] == "knee_xray_model"
        assert data["status"] == "success"
        assert data["inference_time"] >= 0
        assert isinstance(data["device"], str)
    
    def test_ct_analysis_success(self):
        """Test successful CT analysis."""
        files = {"file": ("test_ct.jpg", self.image_bytes, "image/jpeg")}
        
        response = self.client.post("/analyze/ct", files=files)
        
        assert response.status_code == 200
        
        data = response.json()
        assert "request_id" in data
        assert "model_name" in data
        assert "status" in data
        assert "inference_time" in data
        assert "device" in data
        assert "authenticity" in data
        assert "scan_type" in data
        
        # Check structure of authenticity results
        auth = data["authenticity"]
        assert "is_real" in auth
        assert "confidence" in auth
        assert "raw_probability" in auth
        assert isinstance(auth["is_real"], bool)
        assert 0 <= auth["confidence"] <= 1
        assert 0 <= auth["raw_probability"] <= 1
        
        # Check other fields
        assert data["scan_type"] == "CT"
        
        # Check metadata
        assert data["model_name"] == "ct_scan_model"
        assert data["status"] == "success"
        assert data["inference_time"] >= 0
        assert isinstance(data["device"], str)
    
    def test_xray_analysis_invalid_file_type(self):
        """Test X-ray analysis with invalid file type."""
        # Create a text file instead of image
        text_content = b"This is not an image file"
        files = {"file": ("test.txt", text_content, "text/plain")}
        
        response = self.client.post("/analyze/xray", files=files)
        
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
        assert "message" in data
        assert "request_id" in data
        assert data["error"] == "File validation failed"
    
    def test_ct_analysis_invalid_file_type(self):
        """Test CT analysis with invalid file type."""
        # Create a text file instead of image
        text_content = b"This is not an image file"
        files = {"file": ("test.txt", text_content, "text/plain")}
        
        response = self.client.post("/analyze/ct", files=files)
        
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
        assert "message" in data
        assert "request_id" in data
        assert data["error"] == "File validation failed"
    
    def test_xray_analysis_no_file(self):
        """Test X-ray analysis without file."""
        response = self.client.post("/analyze/xray")
        
        assert response.status_code == 422  # Validation error
    
    def test_ct_analysis_no_file(self):
        """Test CT analysis without file."""
        response = self.client.post("/analyze/ct")
        
        assert response.status_code == 422  # Validation error
    
    def test_xray_analysis_large_file(self):
        """Test X-ray analysis with oversized file."""
        settings = get_settings()
        
        # Create a large image (simulate large file)
        large_img_array = np.random.randint(0, 255, (1000, 1000, 3), dtype=np.uint8)
        large_image = Image.fromarray(large_img_array)
        
        # Convert to bytes
        large_image_bytes = io.BytesIO()
        large_image.save(large_image_bytes, format='JPEG', quality=100)
        large_image_bytes.seek(0)
        
        # Mock file size by temporarily reducing max file size
        original_max_size = settings.max_file_size
        settings.max_file_size = 1000  # 1KB limit for testing
        
        try:
            files = {"file": ("large_image.jpg", large_image_bytes, "image/jpeg")}
            response = self.client.post("/analyze/xray", files=files)
            
            assert response.status_code == 400
            
            data = response.json()
            assert "error" in data
            assert data["error"] == "File validation failed"
            
        finally:
            # Restore original max file size
            settings.max_file_size = original_max_size
    
    def test_cors_headers(self):
        """Test CORS headers are present."""
        # Test preflight request
        response = self.client.options("/analyze/xray", headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        })
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        
        # Test actual request
        files = {"file": ("test_xray.jpg", self.image_bytes, "image/jpeg")}
        response = self.client.post("/analyze/xray", files=files, headers={
            "Origin": "http://localhost:5173"
        })
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers


class TestRootEndpoint:
    """Test cases for root endpoint."""
    
    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint returns basic info."""
        response = self.client.get("/")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data
        
        assert data["message"] == "Medical Deepfake Backend API"
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"
