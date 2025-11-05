"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Router for image metadata extraction endpoints.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from models.image_metadata import MetadataResponse
from services.metadata_extractor import MetadataExtractorService
from services.webhook_service import WebhookService
from utils.logger_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["metadata"])


@router.post("/extract-metadata", response_model=MetadataResponse)
async def extract_metadata(
    background_tasks: BackgroundTasks, file: UploadFile = File(...)
) -> JSONResponse:
    """
    Extract metadata from uploaded image file.

    This endpoint receives an image file, extracts its metadata,
    returns it to the client, and sends it to a configured webhook.

    Args:
        background_tasks: FastAPI background tasks
        file: Uploaded image file

    Returns:
        JSON response with extracted metadata

    Raises:
        HTTPException: If file is not an image or processing fails
    """
    # Validate content type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, detail="Arquivo deve ser uma imagem válida"
        )

    logger.info(f"Processando imagem: {file.filename}")

    # Read file bytes
    image_bytes = await file.read()

    # Extract metadata using service
    extractor = MetadataExtractorService()
    metadata = extractor.extract_metadata(
        image_bytes=image_bytes, filename=file.filename, content_type=file.content_type
    )

    # Send to webhook in background
    webhook_service = WebhookService()
    background_tasks.add_task(webhook_service.send_metadata, metadata)

    logger.info(f"Metadados extraídos com sucesso: {file.filename}")

    return JSONResponse(
        status_code=200,
        content=MetadataResponse(
            success=True, metadata=metadata, message="Metadados extraídos com sucesso"
        ).model_dump(mode="json"),
    )
