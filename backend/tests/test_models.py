"""Unit tests for model classes."""

import pytest
import torch
from PIL import Image
import numpy as np
from pathlib import Path

from app.models import KneeXRayModel, CTScanModel


class TestKneeXRayModel:
    """Test cases for KneeXRayModel."""
    
    @pytest.fixture
    def model(self):
        """Create model instance for testing."""
        return KneeXRayModel(device="cpu")
    
    @pytest.fixture
    def sample_image(self):
        """Create a sample image for testing."""
        # Create a simple RGB image
        img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        return Image.fromarray(img_array)
    
    def test_model_initialization(self, model):
        """Test model initialization."""
        assert model.model_name == "knee_xray_model"
        assert model.device == "cpu"
        assert model.model is None
        assert len(model.arthritis_labels) == 4
    
    def test_load_model(self, model, tmp_path):
        """Test model loading."""
        model_path = tmp_path / "test_model.pth"
        model_path.touch()  # Create empty file
        
        # Should not raise exception even with empty file (mock implementation)
        model.load_model(str(model_path))
        
        assert model.model is not None
    
    def test_preprocess(self, model, sample_image):
        """Test image preprocessing."""
        # Load mock model first
        model.model = torch.nn.Module()  # Dummy module
        
        tensor = model.preprocess(sample_image)
        
        assert isinstance(tensor, torch.Tensor)
        assert tensor.shape == (1, 3, 224, 224)
        assert tensor.device.type == "cpu"
    
    def test_predict(self, model, sample_image):
        """Test model prediction."""
        # Load mock model
        model.model = torch.nn.Module()
        
        # Preprocess image
        input_tensor = model.preprocess(sample_image)
        
        # Run prediction
        output = model.predict(input_tensor)
        
        assert isinstance(output, torch.Tensor)
        assert output.shape == (1, 5)  # 1 authenticity + 4 arthritis classes
    
    def test_postprocess(self, model):
        """Test output postprocessing."""
        # Create mock output
        output = torch.randn(1, 5)
        
        results = model.postprocess(output)
        
        assert "authenticity" in results
        assert "arthritis" in results
        
        # Check authenticity structure
        auth = results["authenticity"]
        assert "is_real" in auth
        assert "confidence" in auth
        assert "raw_probability" in auth
        assert 0 <= auth["confidence"] <= 1
        assert 0 <= auth["raw_probability"] <= 1
        
        # Check arthritis structure
        arthritis = results["arthritis"]
        assert "severity" in arthritis
        assert "class_id" in arthritis
        assert "confidence" in arthritis
        assert "probabilities" in arthritis
        assert len(arthritis["probabilities"]) == 4
    
    def test_analyze_complete_pipeline(self, model, sample_image, tmp_path):
        """Test complete analysis pipeline."""
        # Save sample image
        image_path = tmp_path / "test_image.jpg"
        sample_image.save(image_path)
        
        # Load mock model
        model.model = torch.nn.Module()
        
        # Run analysis
        results = model.analyze(str(image_path))
        
        assert "model_name" in results
        assert "status" in results
        assert "inference_time" in results
        assert "device" in results
        assert "authenticity" in results
        assert "arthritis" in results
        
        assert results["model_name"] == "knee_xray_model"
        assert results["device"] == "cpu"
        assert results["status"] == "success"
        assert results["inference_time"] >= 0


class TestCTScanModel:
    """Test cases for CTScanModel."""
    
    @pytest.fixture
    def model(self):
        """Create model instance for testing."""
        return CTScanModel(device="cpu")
    
    @pytest.fixture
    def sample_image(self):
        """Create a sample image for testing."""
        # Create a simple RGB image
        img_array = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        return Image.fromarray(img_array)
    
    def test_model_initialization(self, model):
        """Test model initialization."""
        assert model.model_name == "ct_scan_model"
        assert model.device == "cpu"
        assert model.model is None
    
    def test_load_model(self, model, tmp_path):
        """Test model loading."""
        model_path = tmp_path / "test_model.pth"
        model_path.touch()  # Create empty file
        
        model.load_model(str(model_path))
        
        assert model.model is not None
    
    def test_preprocess(self, model, sample_image):
        """Test image preprocessing."""
        # Load mock model first
        model.model = torch.nn.Module()  # Dummy module
        
        tensor = model.preprocess(sample_image)
        
        assert isinstance(tensor, torch.Tensor)
        assert tensor.shape == (1, 3, 256, 256)
        assert tensor.device.type == "cpu"
    
    def test_predict(self, model, sample_image):
        """Test model prediction."""
        # Load mock model
        model.model = torch.nn.Module()
        
        # Preprocess image
        input_tensor = model.preprocess(sample_image)
        
        # Run prediction
        output = model.predict(input_tensor)
        
        assert isinstance(output, torch.Tensor)
        assert output.shape == (1, 1)  # Binary classification
    
    def test_postprocess(self, model):
        """Test output postprocessing."""
        # Create mock output
        output = torch.randn(1, 1)
        
        results = model.postprocess(output)
        
        assert "authenticity" in results
        assert "scan_type" in results
        assert "analysis_notes" in results
        
        # Check authenticity structure
        auth = results["authenticity"]
        assert "is_real" in auth
        assert "confidence" in auth
        assert "raw_probability" in auth
        assert 0 <= auth["confidence"] <= 1
        assert 0 <= auth["raw_probability"] <= 1
        
        # Check other fields
        assert results["scan_type"] == "CT"
        assert isinstance(results["analysis_notes"], str)
    
    def test_analyze_complete_pipeline(self, model, sample_image, tmp_path):
        """Test complete analysis pipeline."""
        # Save sample image
        image_path = tmp_path / "test_image.jpg"
        sample_image.save(image_path)
        
        # Load mock model
        model.model = torch.nn.Module()
        
        # Run analysis
        results = model.analyze(str(image_path))
        
        assert "model_name" in results
        assert "status" in results
        assert "inference_time" in results
        assert "device" in results
        assert "authenticity" in results
        
        assert results["model_name"] == "ct_scan_model"
        assert results["device"] == "cpu"
        assert results["status"] == "success"
        assert results["inference_time"] >= 0
