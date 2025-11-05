"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Application settings and configuration.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        APP_NAME: Application name
        APP_VERSION: Application version
        DEBUG: Debug mode flag
        WEBHOOK_URL: URL for webhook notifications
        WEBHOOK_TIMEOUT: Webhook request timeout in seconds
        LOG_LEVEL: Logging level
        MAX_FILE_SIZE: Maximum file size in bytes
    """

    APP_NAME: str = "Image Metadata API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    WEBHOOK_URL: Optional[str] = None
    WEBHOOK_TIMEOUT: float = 10.0

    LOG_LEVEL: str = "INFO"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = True


settings = Settings()
