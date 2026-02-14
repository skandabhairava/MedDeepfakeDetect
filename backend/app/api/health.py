"""Health check API endpoints."""

from datetime import datetime
from fastapi import APIRouter

from ..core.config import get_settings
from ..core.logging import get_logger
from ..schemas import HealthResponse
from ..services import ModelService, queue_service

router = APIRouter(tags=["health"])
logger = get_logger("api.health")
model_service = ModelService()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check application health status.
    
    Returns:
        Health status information including model loading status
    """
    settings = get_settings()
    
    try:
        # Get model service health
        model_health = model_service.health_check()
        
        # Get queue service health
        queue_health = queue_service.health_check()
        
        response = HealthResponse(
            status="healthy",
            version=settings.app_version,
            models_loaded=model_health["models_loaded"],
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
        # Add queue health info to response
        response_dict = response.dict()
        response_dict["queue_service"] = queue_health
        
        logger.info(
            "health_check_completed",
            status=response.status,
            models_loaded=response.models_loaded,
            model_count=model_health["model_count"],
            queue_processor_running=queue_health["queue_processor_running"]
        )
        
        return response_dict
        
    except Exception as e:
        logger.error(
            "health_check_failed",
            error=str(e)
        )
        
        return HealthResponse(
            status="unhealthy",
            version=settings.app_version,
            models_loaded=False,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
