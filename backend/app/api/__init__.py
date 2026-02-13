"""API endpoints."""

from .analyze import router as analyze_router
from .health import router as health_router
from .auth import router as auth_router

__all__ = ["analyze_router", "health_router", "auth_router"]
