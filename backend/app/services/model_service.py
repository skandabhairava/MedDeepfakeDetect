"""Model management and inference service."""

import os
from pathlib import Path
from typing import Dict, Optional
import uuid

from ..core.config import get_settings
from ..core.logging import get_logger
from ..models import MainModel


class ModelService:
    """Service for managing models and running inference."""
    
    def __init__(self):
        """Initialize model service."""
        self.settings = get_settings()
        self.logger = get_logger("model_service")
        
        # Model registry
        self.models: Dict[str, MainModel] = {}
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self) -> None:
        """Initialize all models."""
        try:
            # Create model directory if it doesn't exist
            model_dir = Path(self.settings.model_dir)
            model_dir.mkdir(exist_ok=True)
            
            # Initialize knee X-ray model
            xray_model = MainModel(model_name="knee_xray_model", device=self.settings.device)
            xray_model.load_model(str(model_dir / "knee_xray_model.pth"))
            self.models["knee_xray"] = xray_model
            
            # Initialize CT scan model
            ct_model = MainModel(model_name="ct_scan_model", device=self.settings.device)
            # ct_model.load_model(str(model_dir / "ct_scan_model.pth"))
            ct_model.load_model(str(model_dir / "ct_new_arch_model.pth"))
            self.models["ct_scan"] = ct_model
            
            self.logger.info("All models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize models: {str(e)}")
            raise
    
    def analyze_xray(self, image_path: str) -> Dict:
        """Analyze knee X-ray image.
        
        Args:
            image_path: Path to X-ray image file
            
        Returns:
            Analysis results
        """
        request_id = str(uuid.uuid4())
        
        try:
            model = self.models["knee_xray"]
            results = model.analyze(image_path)
            results["request_id"] = request_id
            
            self.logger.info(
                "xray_analysis_completed",
                request_id=request_id,
                image_path=image_path,
                status=results.get("status", "unknown")
            )
            
            return results
            
        except Exception as e:
            self.logger.error(
                "xray_analysis_failed",
                request_id=request_id,
                image_path=image_path,
                error=str(e)
            )
            
            return {
                "request_id": request_id,
                "model_name": "knee_xray_model",
                "status": "error",
                "error": str(e),
                "inference_time": 0.0,
                "device": self.settings.device
            }
    
    def analyze_ct_scan(self, image_path: str) -> Dict:
        """Analyze CT scan image.
        
        Args:
            image_path: Path to CT scan image file
            
        Returns:
            Analysis results
        """
        request_id = str(uuid.uuid4())
        
        try:
            model = self.models["ct_scan"]
            results = model.analyze(image_path)
            results["request_id"] = request_id
            
            self.logger.info(
                "ct_analysis_completed",
                request_id=request_id,
                image_path=image_path,
                status=results.get("status", "unknown")
            )
            
            return results
            
        except Exception as e:
            self.logger.error(
                "ct_analysis_failed",
                request_id=request_id,
                image_path=image_path,
                error=str(e)
            )
            
            return {
                "request_id": request_id,
                "model_name": "ct_scan_model",
                "status": "error",
                "error": str(e),
                "inference_time": 0.0,
                "device": self.settings.device
            }
    
    def get_model_status(self) -> Dict[str, bool]:
        """Get status of all models.
        
        Returns:
            Dictionary with model names and their loaded status
        """
        return {
            name: model is not None 
            for name, model in self.models.items()
        }
    
    def health_check(self) -> Dict:
        """Perform health check on model service.
        
        Returns:
            Health status information
        """
        return {
            "models_loaded": len(self.models) > 0,
            "model_count": len(self.models),
            "model_status": self.get_model_status(),
            "device": self.settings.device
        }
