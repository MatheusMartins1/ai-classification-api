"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Service for sending metadata to webhooks.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

from typing import Optional

import httpx

from config.settings import settings
from models.image_metadata import ImageMetadata, WebhookPayload
from utils.logger_config import get_logger

logger = get_logger(__name__)


class WebhookService:
    """
    Service responsible for sending data to external webhooks.

    This service handles HTTP communication with webhook endpoints
    following Single Responsibility Principle.
    """

    def __init__(self, webhook_url: Optional[str] = None):
        """
        Initialize webhook service.

        Args:
            webhook_url: Custom webhook URL, defaults to settings
        """
        self.webhook_url = webhook_url or settings.WEBHOOK_URL
        self.timeout = settings.WEBHOOK_TIMEOUT

    async def send_metadata(self, metadata: ImageMetadata) -> bool:
        """
        Send image metadata to configured webhook.

        Args:
            metadata: Image metadata to send

        Returns:
            True if successful, False otherwise
        """
        if not self.webhook_url:
            logger.warning("Webhook URL não configurada")
            return False

        try:
            payload = WebhookPayload(metadata=metadata, event_type="metadata_extracted")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.webhook_url, json=payload.model_dump(mode="json")
                )
                response.raise_for_status()

            logger.info(f"Metadados enviados para webhook: {self.webhook_url}")
            return True

        except httpx.TimeoutException:
            logger.error("Timeout ao enviar para webhook")
            return False
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao enviar para webhook: {e.response.status_code}")
            return False
        except Exception as e:
            logger.error(f"Erro ao enviar para webhook: {str(e)}")
            return False
