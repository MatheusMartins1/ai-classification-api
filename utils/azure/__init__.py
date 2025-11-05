"""
@fileoverview Azure Services Module
@description Azure services integration for the project
@author Matheus Martins
@created 2025-11-04
@lastmodified 2025-11-04
"""

from utils.azure.azure_service import AzureService
from utils.azure.blob_storage import BlobStorageService
from utils.azure.exceptions import (
    AzureError,
    AzureConnectionError,
    AzureAuthenticationError,
    BlobStorageError,
    BlobNotFoundError,
    BlobUploadError,
    BlobDownloadError,
    BlobDeleteError,
    ContainerNotFoundError,
    ContainerCreationError,
)


__all__ = [
    "AzureService",
    "BlobStorageService",
    "AzureError",
    "AzureConnectionError",
    "AzureAuthenticationError",
    "BlobStorageError",
    "BlobNotFoundError",
    "BlobUploadError",
    "BlobDownloadError",
    "BlobDeleteError",
    "ContainerNotFoundError",
    "ContainerCreationError",
]
