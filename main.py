"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Main application entry point for Image Metadata API.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from routers import metadata
from utils.logger_config import get_logger

logger = get_logger(__name__)


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.APP_NAME, version=settings.APP_VERSION, debug=settings.DEBUG
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(metadata.router)

    return app


app = create_application()


@app.get("/", tags=["health"])
async def root() -> dict:
    """
    Root endpoint for API health check.

    Returns:
        API status information
    """
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
    }


@app.get("/health", tags=["health"])
async def health() -> dict:
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")

    uvicorn.run("main:app", host="0.0.0.0", port=8345, reload=settings.DEBUG)
