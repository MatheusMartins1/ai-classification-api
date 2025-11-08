"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Application settings and configuration.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings

from utils.env import load_env_file

# Determine base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
env_file_path = load_env_file(BASE_DIR)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        APP_NAME: Application name
        APP_VERSION: Application version
        DEBUG: Debug mode flag
        PORT: Application port
        WEBHOOK_URL: URL for webhook notifications
        WEBHOOK_TIMEOUT: Webhook request timeout in seconds
        LOG_LEVEL: Logging level
        MAX_FILE_SIZE: Maximum file size in bytes
        SUPABASE_URL: Supabase project URL
        SUPABASE_KEY: Supabase API key
        MOCK_CAMERA: Enable mock camera for testing
    """

    BASE_DIR: Path = BASE_DIR

    APP_NAME: str = "Image Metadata API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    PORT: int = int(os.getenv("PORT", "8345"))

    WEBHOOK_URL: Optional[str] = os.getenv("WEBHOOK_URL")
    WEBHOOK_TIMEOUT: float = float(os.getenv("WEBHOOK_TIMEOUT", "10.0"))

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MAX_FILE_SIZE: int = 1 * 1024 * 1024 * 1024  # 1GB

    # Supabase Configuration
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")

    # API Key for authentication
    API_KEY: Optional[str] = os.getenv("API_KEY")

    MOCK_CAMERA: bool = os.getenv("MOCK_CAMERA", "false").lower() == "true"

    class Config:
        """Pydantic configuration."""

        case_sensitive = True


settings = Settings()
