"""Structured logging configuration."""

import structlog
from typing import Any, Dict

from .config import get_settings


def configure_logging() -> None:
    """Configure structured logging."""
    settings = get_settings()
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.log_format == "json" 
            else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def log_request_info(request_id: str, method: str, path: str, **kwargs: Any) -> None:
    """Log request information."""
    logger = get_logger("request")
    logger.info(
        "request_started",
        request_id=request_id,
        method=method,
        path=path,
        **kwargs
    )


def log_inference_info(
    request_id: str,
    model_name: str,
    inference_time: float,
    **kwargs: Any
) -> None:
    """Log inference information."""
    logger = get_logger("inference")
    logger.info(
        "inference_completed",
        request_id=request_id,
        model_name=model_name,
        inference_time=inference_time,
        **kwargs
    )
