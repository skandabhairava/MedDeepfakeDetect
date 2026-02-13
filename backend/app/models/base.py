"""Base model interface for medical image analysis."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple
import time
from pathlib import Path
import numpy as np
from PIL import Image
import torch

from ..core.logging import get_logger


class BaseModel(ABC):
    """Abstract base class for medical image analysis models."""
    
    def __init__(self, model_name: str, device: str = "cpu"):
        """Initialize model.
        
        Args:
            model_name: Name of the model
            device: Device for inference ('cpu' or 'cuda')
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self.logger = get_logger(f"model.{model_name}")
        
    @abstractmethod
    def load_model(self, model_path: str) -> None:
        """Load model from checkpoint.
        
        Args:
            model_path: Path to model checkpoint
        """
        pass
    
    @abstractmethod
    def preprocess(self, image: Image.Image) -> torch.Tensor:
        """Preprocess image for model input.
        
        Args:
            image: PIL Image
            
        Returns:
            Preprocessed tensor
        """
        pass
    
    @abstractmethod
    def predict(self, input_tensor: torch.Tensor) -> torch.Tensor:
        """Run model inference.
        
        Args:
            input_tensor: Preprocessed input tensor
            
        Returns:
            Model output tensor
        """
        pass
    
    @abstractmethod
    def postprocess(self, output: torch.Tensor) -> Dict[str, Any]:
        """Postprocess model output.
        
        Args:
            output: Raw model output
            
        Returns:
            Processed results dictionary
        """
        pass
    
    def analyze(self, image_path: str) -> Dict[str, Any]:
        """Complete analysis pipeline.
        
        Args:
            image_path: Path to input image
            
        Returns:
            Analysis results with metadata
        """
        start_time = time.time()
        
        try:
            # Load and validate image
            image = self._load_image(image_path)
            
            # Preprocess
            input_tensor = self.preprocess(image)
            
            # Predict
            output = self.predict(input_tensor)
            
            # Postprocess
            results = self.postprocess(output)
            
            # Add metadata
            inference_time = time.time() - start_time
            results.update({
                "model_name": self.model_name,
                "inference_time": round(inference_time, 3),
                "device": self.device,
                "status": "success"
            })
            
            self.logger.info(
                "analysis_completed",
                model_name=self.model_name,
                inference_time=inference_time,
                image_path=image_path
            )
            
            return results
            
        except Exception as e:
            self.logger.error(
                "analysis_failed",
                model_name=self.model_name,
                error=str(e),
                image_path=image_path
            )
            return {
                "model_name": self.model_name,
                "status": "error",
                "error": str(e),
                "inference_time": round(time.time() - start_time, 3)
            }
    
    def _load_image(self, image_path: str) -> Image.Image:
        """Load and validate image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            PIL Image
            
        Raises:
            ValueError: If image cannot be loaded
        """
        try:
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            return image
            
        except Exception as e:
            raise ValueError(f"Cannot load image {image_path}: {str(e)}")
