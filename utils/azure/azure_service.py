"""
@fileoverview Azure Service Manager
@description Main class to manage all Azure services
@author Matheus Martins
@created 2025-11-04
@lastmodified 2025-11-04
"""

import os
from typing import Optional

from utils.azure.blob_storage import BlobStorageService
from utils.azure.exceptions import AzureAuthenticationError
from utils.LoggerConfig import LoggerConfig


logger = LoggerConfig.add_file_logger(
    name="azure_service", filename=None, dir_name=None, prefix="azure"
)


class AzureService:
    """
    Main Azure service manager.
    Single responsibility: Manage and provide access to all Azure services.
    """

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        connection_string: Optional[str] = None,
        account_name: Optional[str] = None,
        account_key: Optional[str] = None,
    ) -> None:
        """
        Initialize Azure service manager.

        Args:
            connection_string (Optional[str]): Azure Storage connection string
            account_name (Optional[str]): Azure Storage account name
            account_key (Optional[str]): Azure Storage account key

        Raises:
            AzureAuthenticationError: When credentials are missing
        """
        if self._initialized:
            return

        self._connection_string = connection_string or os.getenv(
            "AZURE_STORAGE_CONNECTION_STRING"
        )
        self._account_name = account_name or os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        self._account_key = account_key or os.getenv("AZURE_STORAGE_ACCOUNT_KEY")

        if not self._connection_string and not (
            self._account_name and self._account_key
        ):
            error_msg = "Azure credentials not found in environment variables"
            logger.error(error_msg)
            raise AzureAuthenticationError(error_msg)

        self._blob_storage = None
        self._initialized = True

        logger.info("Azure service manager initialized")

    @property
    def blob_storage(self) -> BlobStorageService:
        """
        Get Blob Storage service instance.

        Returns:
            BlobStorageService: Blob Storage service instance
        """
        if self._blob_storage is None:
            self._blob_storage = BlobStorageService(
                connection_string=self._connection_string,
                account_name=self._account_name,
                account_key=self._account_key,
            )
            logger.info("Blob Storage service initialized")

        return self._blob_storage

    def reset(self) -> None:
        """Reset all service instances."""
        self._blob_storage = None
        logger.info("Azure services reset")

