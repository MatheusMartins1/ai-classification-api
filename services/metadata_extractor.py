"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Service for extracting metadata from images.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

import io
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import HTTPException
from PIL import Image
from PIL.ExifTags import TAGS

from models.image_metadata import ImageMetadata, ImageSize


class MetadataExtractorService:
    """
    Service responsible for extracting metadata from image files.

    This service handles image processing and metadata extraction
    following Single Responsibility Principle.
    """

    @staticmethod
    def extract_metadata(
        image_bytes: bytes, filename: str, content_type: str
    ) -> ImageMetadata:
        """
        Extract comprehensive metadata from image bytes.

        Args:
            image_bytes: Raw image bytes
            filename: Original filename
            content_type: MIME content type

        Returns:
            ImageMetadata: Extracted metadata object

        Raises:
            HTTPException: If image processing fails
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))

            # Extract basic metadata
            size = ImageSize(width=image.width, height=image.height)

            # Extract EXIF data
            exif_data = MetadataExtractorService._extract_exif(image)

            # Extract additional info
            info_data = MetadataExtractorService._extract_info(image)

            return ImageMetadata(
                format=image.format,
                mode=image.mode,
                size=size,
                file_size_bytes=len(image_bytes),
                filename=filename,
                content_type=content_type,
                timestamp=datetime.utcnow(),
                exif=exif_data if exif_data else None,
                info=info_data if info_data else None,
            )

        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Erro ao processar imagem: {str(e)}"
            )

    @staticmethod
    def _extract_exif(image: Image.Image) -> Optional[Dict[str, Any]]:
        """
        Extract EXIF metadata from image.

        Args:
            image: PIL Image object

        Returns:
            Dictionary with EXIF data or None
        """
        exif_data = {}

        try:
            if hasattr(image, "_getexif") and image._getexif():
                exif = image._getexif()
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    try:
                        exif_data[tag] = str(value)
                    except Exception:
                        pass
        except Exception:
            pass

        return exif_data if exif_data else None

    @staticmethod
    def _extract_info(image: Image.Image) -> Optional[Dict[str, Any]]:
        """
        Extract additional image information.

        Args:
            image: PIL Image object

        Returns:
            Dictionary with additional info or None
        """
        info_data = {}

        try:
            if hasattr(image, "info") and image.info:
                info_data = {k: str(v) for k, v in image.info.items()}
        except Exception:
            pass

        return info_data if info_data else None
