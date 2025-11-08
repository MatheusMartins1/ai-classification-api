"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: API Key authentication dependency for FastAPI routes.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

import os

from fastapi import Header, HTTPException, status


async def verify_api_key(x_api_key: str = Header(...)) -> str:
    """
    Verify API key from request header.

    Args:
        x_api_key: API key from X-API-Key header

    Returns:
        The validated API key

    Raises:
        HTTPException: If API key is missing or invalid
    """
    api_key = os.getenv("API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API Key não configurada no servidor",
        )

    if x_api_key != api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida",
        )

    return x_api_key
