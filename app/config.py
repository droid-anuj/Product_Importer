"""
Application configuration settings.
Loads from environment variables with sensible defaults.
"""

import os
from functools import lru_cache


class Settings:
    """Application settings from environment variables."""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/product_importer"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
    
    # Application
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    API_TITLE: str = "Product Importer API"
    API_VERSION: str = "1.0.0"
    
    # Upload settings
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB
    BATCH_SIZE: int = 10000  # Process 10k rows at a time
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/tmp/uploads")
    
    # Webhook settings
    WEBHOOK_TIMEOUT: int = 10
    WEBHOOK_RETRIES: int = 3


@lru_cache
def get_settings() -> Settings:
    """Get application settings (cached)."""
    return Settings()
