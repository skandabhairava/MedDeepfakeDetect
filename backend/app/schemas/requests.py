"""Request schemas for API endpoints."""

from typing import Optional
from pydantic import BaseModel, Field


class BaseAnalysisRequest(BaseModel):
    """Base schema for analysis requests."""
    
    class Config:
        """Pydantic configuration."""
        extra = "forbid"


class HealthResponse(BaseModel):
    """Health check response schema."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    models_loaded: bool = Field(..., description="Whether models are loaded")
    timestamp: str = Field(..., description="Current timestamp")


class AnalysisResponse(BaseModel):
    """Base schema for analysis responses."""
    
    request_id: str = Field(..., description="Unique request identifier")
    model_name: str = Field(..., description="Name of the model used")
    status: str = Field(..., description="Analysis status")
    inference_time: float = Field(..., description="Inference time in seconds")
    device: str = Field(..., description="Device used for inference")
    
    # Results
    authenticity: dict = Field(..., description="Authenticity analysis results")
    
    # Optional additional analysis
    arthritis: Optional[dict] = Field(None, description="Arthritis classification results")
    scan_type: Optional[str] = Field(None, description="Type of medical scan")
    
    # Error information
    error: Optional[str] = Field(None, description="Error message if analysis failed")
    
    class Config:
        """Pydantic configuration."""
        extra = "forbid"
        json_encoders = {
            # Handle numpy types if needed
        }
