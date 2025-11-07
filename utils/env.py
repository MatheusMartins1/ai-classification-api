"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Environment configuration loader with Docker support.
"""

import os
import platform
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


def load_env_file(BASE_DIR: Optional[Path] = None, use_prod: bool = False) -> str:
    """
    Load environment variables from .env file.

    Args:
        BASE_DIR: Base directory path. If None, uses parent of this file.
        use_prod: Force production environment. Defaults to False.

    Returns:
        Path to the loaded .env file.
    """
    if BASE_DIR is None:
        BASE_DIR = Path(__file__).resolve().parent.parent

    # Get system user safely (Docker-compatible)
    try:
        system_user = os.getlogin()
    except (OSError, AttributeError):
        # Fallback for Docker/non-TTY environments
        system_user = os.getenv("USER") or os.getenv("USERNAME") or "docker"

    # Detect environment
    is_docker = os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER") == "true"
    is_windows = platform.system() == "Windows"
    is_dev_user = system_user in ["Matheus", "Dev", "Matheus Martins"]

    is_dev_environment = is_windows and is_dev_user and not is_docker

    # Load Redis password updater for production/docker
    if use_prod or not is_dev_environment:
        try:
            from utils import update_redis_password  # type: ignore

            update_redis_password.main()
        except Exception as e:
            print(f"Aviso ao carregar update_redis_password: {e}")

    # Determine which .env file to load
    if is_dev_environment and not use_prod:
        dotenv_path = os.path.join(BASE_DIR, ".env.dev")
        env_type = "development"
    elif use_prod or is_docker:
        dotenv_path = os.path.join(BASE_DIR, ".env.prod")
        env_type = "production"
    else:
        dotenv_path = os.path.join(BASE_DIR, ".env.homol")
        env_type = "homologation"

    # Load environment variables
    load_dotenv(dotenv_path, override=True)

    print(f"Environment: {env_type} | User: {system_user} | Docker: {is_docker}")
    print(f"Loaded: {dotenv_path}")

    return dotenv_path
