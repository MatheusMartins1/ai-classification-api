"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Centralized logging configuration.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

import logging
import sys
from typing import Optional

from config.settings import settings


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get configured logger instance.

    Args:
        name: Logger name (typically __name__)
        level: Optional log level override

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        # Set log level
        log_level = level or settings.LOG_LEVEL
        logger.setLevel(getattr(logging, log_level.upper()))

        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, log_level.upper()))

        # Create formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

    return logger
