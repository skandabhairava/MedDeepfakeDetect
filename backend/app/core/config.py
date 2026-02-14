"""Application configuration settings."""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = Field(default="Medical Deepfake Backend", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # Rate limiting
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per window")
    rate_limit_window: int = Field(default=3600, description="Rate limit window in seconds")
    
    # File upload
    max_file_size: int = Field(default=10485760, description="Max file size in bytes (10MB)")
    upload_dir: str = Field(default="uploads", description="Upload directory")
    allowed_extensions: List[str] = Field(
        default=["jpg", "jpeg", "png"],
        description="Allowed file extensions"
    )
    
    # Model settings
    model_dir: str = Field(default="models", description="Model directory")
    inference_timeout: int = Field(default=30, description="Inference timeout in seconds")
    device: str = Field(default="cpu", description="Device for inference")
    
    # Queue and thread pool settings
    max_worker_threads: int = Field(default=4, description="Maximum number of worker threads")
    queue_size_limit: int = Field(default=100, description="Maximum queue size")
    queue_check_interval: int = Field(default=2, description="Queue status check interval in seconds")
    
    # Analysis rate limiting
    analysis_rate_limit_seconds: int = Field(default=5, description="Minimum seconds between analyses per user")
    
    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(default="json", description="Log format")
    
    # Authentication
    secret_key: str = Field(default="your-secret-key-change-in-production", description="JWT secret key")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration in minutes")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
