"""Main FastAPI application."""

import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.api import analyze_router, health_router, auth_router


# Configure logging
configure_logging()
logger = get_logger("main")

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Global instances
model_service = None
queue_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Medical Deepfake Backend")
    
    settings = get_settings()
    
    try:
        # Initialize model service
        from app.services import ModelService, queue_service
        global model_service, queue_service
        model_service = ModelService()
        
        # Queue service is automatically initialized on import
        logger.info("Model service and queue service initialized")
        
        logger.info("Application startup completed")
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Medical Deepfake Backend")
    
    # Stop queue service
    if queue_service:
        try:
            queue_service.stop_queue_processor()
            logger.info("Queue service stopped")
        except Exception as e:
            logger.error(f"Error stopping queue service: {str(e)}")


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Medical image authenticity analysis API",
        debug=settings.debug,
        lifespan=lifespan
    )
    
    # Add rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Add Gzip middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Include routers
    app.include_router(analyze_router)
    app.include_router(health_router)
    app.include_router(auth_router)
    
    # Root endpoint (fallback if frontend not built)
    @app.get("/api")
    async def api_root():
        """API root endpoint."""
        return {
            "message": "Medical Deepfake Backend API",
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health"
        }
    
    # Serve static files (frontend build)
    frontend_build_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "build")
    if os.path.exists(frontend_build_path):
        # Serve entire build from root with SPA fallback
        app.mount("/", StaticFiles(directory=frontend_build_path, html=True), name="static")
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Global exception handler."""
        logger.error(
            "unhandled_exception",
            path=request.url.path,
            method=request.method,
            error=str(exc)
        )
        
        return HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    
    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
