"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Pydantic models for image metadata requests and responses.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ImageSize(BaseModel):
    """
    Image dimensions model.

    Attributes:
        width: Image width in pixels
        height: Image height in pixels
    """

    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")


class ImageMetadata(BaseModel):
    """
    Complete image metadata model.

    Attributes:
        format: Image format (JPEG, PNG, etc)
        mode: Color mode (RGB, RGBA, L, etc)
        size: Image dimensions
        file_size_bytes: File size in bytes
        filename: Original filename
        content_type: MIME content type
        timestamp: Processing timestamp
        exif: EXIF metadata if available
        info: Additional image information
    """

    format: Optional[str] = Field(None, description="Image format")
    mode: Optional[str] = Field(None, description="Color mode")
    size: ImageSize = Field(..., description="Image dimensions")
    file_size_bytes: int = Field(..., description="File size in bytes")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME content type")
    timestamp: datetime = Field(..., description="Processing timestamp")
    exif: Optional[Dict[str, Any]] = Field(None, description="EXIF metadata")
    info: Optional[Dict[str, Any]] = Field(None, description="Additional info")


class MetadataResponse(BaseModel):
    """
    API response model for metadata extraction.

    Attributes:
        success: Operation success status
        metadata: Extracted metadata
        message: Optional message
    """

    success: bool = Field(..., description="Operation success status")
    metadata: ImageMetadata = Field(..., description="Extracted metadata")
    message: Optional[str] = Field(None, description="Optional message")


class WebhookPayload(BaseModel):
    """
    Webhook payload model.

    Attributes:
        metadata: Image metadata to send
        event_type: Type of event
    """

    metadata: ImageMetadata = Field(..., description="Image metadata")
    event_type: str = Field(default="metadata_extracted", description="Event type")
