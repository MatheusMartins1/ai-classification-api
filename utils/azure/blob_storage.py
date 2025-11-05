"""
@fileoverview Azure Blob Storage Service
@description Service class for Azure Blob Storage operations (CRUD)
@author Matheus Martins
@created 2025-11-04
@lastmodified 2025-11-04
"""

import os
import io
from typing import Optional, List, Dict, Any, BinaryIO
from pathlib import Path

from azure.storage.blob import (
    BlobServiceClient,
    BlobClient,
    ContainerClient,
    ContentSettings,
)
from azure.core.exceptions import (
    ResourceNotFoundError,
    ResourceExistsError,
    AzureError as AzureCoreError,
)

from utils.LoggerConfig import LoggerConfig
from utils.azure.exceptions import (
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


logger = LoggerConfig.add_file_logger(
    name="azure_blob_storage", filename=None, dir_name=None, prefix="azure_blob"
)


class BlobStorageService:
    """
    Service class for Azure Blob Storage operations.
    Single responsibility: Handle Blob Storage CRUD operations.
    """

    def __init__(
        self,
        connection_string: Optional[str] = None,
        account_name: Optional[str] = None,
        account_key: Optional[str] = None,
    ) -> None:
        """
        Initialize Blob Storage service.

        Args:
            connection_string (Optional[str]): Azure Storage connection string.
                If not provided, reads from AZURE_STORAGE_CONNECTION_STRING env var.
            account_name (Optional[str]): Azure Storage account name.
                Used if connection_string not provided. Reads from AZURE_STORAGE_ACCOUNT_NAME.
            account_key (Optional[str]): Azure Storage account key.
                Used if connection_string not provided. Reads from AZURE_STORAGE_ACCOUNT_KEY.

        Raises:
            AzureAuthenticationError: When credentials are missing or invalid
            AzureConnectionError: When connection to Azure fails
        """
        self._connection_string = connection_string or os.getenv(
            "AZURE_STORAGE_CONNECTION_STRING"
        )
        self._account_name = account_name or os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        self._account_key = account_key or os.getenv("AZURE_STORAGE_ACCOUNT_KEY")

        if not self._connection_string and not (
            self._account_name and self._account_key
        ):
            error_msg = "Azure Storage credentials not provided. Set AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_ACCOUNT_NAME and AZURE_STORAGE_ACCOUNT_KEY"
            logger.error(error_msg)
            raise AzureAuthenticationError(error_msg)

        try:
            if self._connection_string:
                self._client: BlobServiceClient = BlobServiceClient.from_connection_string(
                    self._connection_string
                )
                logger.info("Blob Storage client initialized with connection string")
            else:
                connection_string = f"DefaultEndpointsProtocol=https;AccountName={self._account_name};AccountKey={self._account_key};EndpointSuffix=core.windows.net"
                self._client = BlobServiceClient.from_connection_string(
                    connection_string
                )
                logger.info(
                    f"Blob Storage client initialized for account: {self._account_name}"
                )

        except Exception as e:
            error_msg = f"Failed to initialize Blob Storage client: {e}"
            logger.error(error_msg)
            raise AzureConnectionError(error_msg)

    def create_container(
        self, container_name: str, public_access: Optional[str] = None
    ) -> bool:
        """
        Create a new container in Blob Storage.

        Args:
            container_name (str): Name of the container to create
            public_access (Optional[str]): Public access level ('blob', 'container', or None)

        Returns:
            bool: True if container created successfully, False if already exists

        Raises:
            ContainerCreationError: When container creation fails
        """
        try:
            container_client = self._client.create_container(
                container_name, public_access=public_access
            )
            logger.info(f"Container created successfully: {container_name}")
            return True

        except ResourceExistsError:
            logger.warning(f"Container already exists: {container_name}")
            return False

        except Exception as e:
            error_msg = f"Failed to create container {container_name}: {e}"
            logger.error(error_msg)
            raise ContainerCreationError(error_msg)

    def delete_container(self, container_name: str) -> bool:
        """
        Delete a container from Blob Storage.

        Args:
            container_name (str): Name of the container to delete

        Returns:
            bool: True if deletion successful

        Raises:
            ContainerNotFoundError: When container doesn't exist
            BlobStorageError: When deletion fails
        """
        try:
            self._client.delete_container(container_name)
            logger.info(f"Container deleted successfully: {container_name}")
            return True

        except ResourceNotFoundError:
            error_msg = f"Container not found: {container_name}"
            logger.error(error_msg)
            raise ContainerNotFoundError(error_msg)

        except Exception as e:
            error_msg = f"Failed to delete container {container_name}: {e}"
            logger.error(error_msg)
            raise BlobStorageError(error_msg)

    def list_containers(self) -> List[Dict[str, Any]]:
        """
        List all containers in the storage account.

        Returns:
            List[Dict[str, Any]]: List of container information dictionaries

        Raises:
            BlobStorageError: When listing fails
        """
        try:
            containers = []
            for container in self._client.list_containers():
                containers.append(
                    {
                        "name": container["name"],
                        "last_modified": container.get("last_modified"),
                        "metadata": container.get("metadata", {}),
                    }
                )

            logger.info(f"Listed {len(containers)} containers")
            return containers

        except Exception as e:
            error_msg = f"Failed to list containers: {e}"
            logger.error(error_msg)
            raise BlobStorageError(error_msg)

    def upload_blob(
        self,
        container_name: str,
        blob_name: str,
        data: Any,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        overwrite: bool = True,
    ) -> str:
        """
        Upload data to a blob.

        Args:
            container_name (str): Name of the container
            blob_name (str): Name of the blob (can include folder structure)
            data (Any): Data to upload (bytes, str, file-like object, or file path)
            content_type (Optional[str]): Content type for the blob
            metadata (Optional[Dict[str, str]]): Metadata to attach to the blob
            overwrite (bool): Whether to overwrite if blob exists

        Returns:
            str: URL of the uploaded blob

        Raises:
            BlobUploadError: When upload fails
        """
        try:
            blob_client = self._client.get_blob_client(
                container=container_name, blob=blob_name
            )

            # Handle different data types
            if isinstance(data, str) and os.path.isfile(data):
                # File path provided
                with open(data, "rb") as file_data:
                    upload_data = file_data.read()
                if not content_type:
                    import mimetypes

                    content_type, _ = mimetypes.guess_type(data)
            elif isinstance(data, (str, bytes)):
                # String or bytes provided
                upload_data = data.encode("utf-8") if isinstance(data, str) else data
            else:
                # Assume file-like object
                upload_data = data

            # Prepare content settings
            content_settings = None
            if content_type:
                content_settings = ContentSettings(content_type=content_type)

            # Upload blob
            blob_client.upload_blob(
                upload_data,
                overwrite=overwrite,
                content_settings=content_settings,
                metadata=metadata,
            )

            blob_url = blob_client.url
            logger.info(
                f"Blob uploaded successfully: {container_name}/{blob_name} -> {blob_url}"
            )
            return blob_url

        except Exception as e:
            error_msg = f"Failed to upload blob {container_name}/{blob_name}: {e}"
            logger.error(error_msg)
            raise BlobUploadError(error_msg)

    def download_blob(
        self,
        container_name: str,
        blob_name: str,
        download_path: Optional[str] = None,
    ) -> Any:
        """
        Download a blob from storage.

        Args:
            container_name (str): Name of the container
            blob_name (str): Name of the blob
            download_path (Optional[str]): Local path to save the file.
                If None, returns bytes data.

        Returns:
            Any: Bytes data if download_path is None, file path if saved to disk

        Raises:
            BlobNotFoundError: When blob doesn't exist
            BlobDownloadError: When download fails
        """
        try:
            blob_client = self._client.get_blob_client(
                container=container_name, blob=blob_name
            )

            # Check if blob exists
            if not blob_client.exists():
                error_msg = f"Blob not found: {container_name}/{blob_name}"
                logger.error(error_msg)
                raise BlobNotFoundError(error_msg)

            # Download blob
            blob_data = blob_client.download_blob()

            if download_path:
                # Save to file
                os.makedirs(os.path.dirname(download_path), exist_ok=True)
                with open(download_path, "wb") as file:
                    file.write(blob_data.readall())
                logger.info(
                    f"Blob downloaded successfully: {container_name}/{blob_name} -> {download_path}"
                )
                return download_path
            else:
                # Return bytes
                data = blob_data.readall()
                logger.info(
                    f"Blob data retrieved: {container_name}/{blob_name} ({len(data)} bytes)"
                )
                return data

        except BlobNotFoundError:
            raise

        except Exception as e:
            error_msg = f"Failed to download blob {container_name}/{blob_name}: {e}"
            logger.error(error_msg)
            raise BlobDownloadError(error_msg)

    def delete_blob(self, container_name: str, blob_name: str) -> bool:
        """
        Delete a blob from storage.

        Args:
            container_name (str): Name of the container
            blob_name (str): Name of the blob

        Returns:
            bool: True if deletion successful

        Raises:
            BlobNotFoundError: When blob doesn't exist
            BlobDeleteError: When deletion fails
        """
        try:
            blob_client = self._client.get_blob_client(
                container=container_name, blob=blob_name
            )

            if not blob_client.exists():
                error_msg = f"Blob not found: {container_name}/{blob_name}"
                logger.error(error_msg)
                raise BlobNotFoundError(error_msg)

            blob_client.delete_blob()
            logger.info(f"Blob deleted successfully: {container_name}/{blob_name}")
            return True

        except BlobNotFoundError:
            raise

        except Exception as e:
            error_msg = f"Failed to delete blob {container_name}/{blob_name}: {e}"
            logger.error(error_msg)
            raise BlobDeleteError(error_msg)

    def list_blobs(
        self, container_name: str, prefix: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all blobs in a container.

        Args:
            container_name (str): Name of the container
            prefix (Optional[str]): Filter blobs by prefix (folder path)

        Returns:
            List[Dict[str, Any]]: List of blob information dictionaries

        Raises:
            ContainerNotFoundError: When container doesn't exist
            BlobStorageError: When listing fails
        """
        try:
            container_client = self._client.get_container_client(container_name)

            if not container_client.exists():
                error_msg = f"Container not found: {container_name}"
                logger.error(error_msg)
                raise ContainerNotFoundError(error_msg)

            blobs = []
            for blob in container_client.list_blobs(name_starts_with=prefix):
                blobs.append(
                    {
                        "name": blob.name,
                        "size": blob.size,
                        "last_modified": blob.last_modified,
                        "content_type": blob.content_settings.content_type
                        if blob.content_settings
                        else None,
                        "metadata": blob.metadata or {},
                    }
                )

            logger.info(
                f"Listed {len(blobs)} blobs in container: {container_name}"
                + (f" with prefix: {prefix}" if prefix else "")
            )
            return blobs

        except ContainerNotFoundError:
            raise

        except Exception as e:
            error_msg = f"Failed to list blobs in container {container_name}: {e}"
            logger.error(error_msg)
            raise BlobStorageError(error_msg)

    def blob_exists(self, container_name: str, blob_name: str) -> bool:
        """
        Check if a blob exists.

        Args:
            container_name (str): Name of the container
            blob_name (str): Name of the blob

        Returns:
            bool: True if blob exists, False otherwise

        Raises:
            BlobStorageError: When check fails
        """
        try:
            blob_client = self._client.get_blob_client(
                container=container_name, blob=blob_name
            )
            exists = blob_client.exists()
            logger.info(
                f"Blob existence check: {container_name}/{blob_name} -> {exists}"
            )
            return exists

        except Exception as e:
            error_msg = (
                f"Failed to check blob existence {container_name}/{blob_name}: {e}"
            )
            logger.error(error_msg)
            raise BlobStorageError(error_msg)

    def get_blob_properties(
        self, container_name: str, blob_name: str
    ) -> Dict[str, Any]:
        """
        Get properties and metadata of a blob.

        Args:
            container_name (str): Name of the container
            blob_name (str): Name of the blob

        Returns:
            Dict[str, Any]: Blob properties and metadata

        Raises:
            BlobNotFoundError: When blob doesn't exist
            BlobStorageError: When retrieval fails
        """
        try:
            blob_client = self._client.get_blob_client(
                container=container_name, blob=blob_name
            )

            if not blob_client.exists():
                error_msg = f"Blob not found: {container_name}/{blob_name}"
                logger.error(error_msg)
                raise BlobNotFoundError(error_msg)

            properties = blob_client.get_blob_properties()

            blob_info = {
                "name": blob_name,
                "container": container_name,
                "size": properties.size,
                "last_modified": properties.last_modified,
                "content_type": properties.content_settings.content_type
                if properties.content_settings
                else None,
                "metadata": properties.metadata or {},
                "etag": properties.etag,
                "url": blob_client.url,
            }

            logger.info(f"Retrieved blob properties: {container_name}/{blob_name}")
            return blob_info

        except BlobNotFoundError:
            raise

        except Exception as e:
            error_msg = (
                f"Failed to get blob properties {container_name}/{blob_name}: {e}"
            )
            logger.error(error_msg)
            raise BlobStorageError(error_msg)

    def copy_blob(
        self,
        source_container: str,
        source_blob: str,
        dest_container: str,
        dest_blob: str,
    ) -> bool:
        """
        Copy a blob from one location to another.

        Args:
            source_container (str): Source container name
            source_blob (str): Source blob name
            dest_container (str): Destination container name
            dest_blob (str): Destination blob name

        Returns:
            bool: True if copy successful

        Raises:
            BlobNotFoundError: When source blob doesn't exist
            BlobStorageError: When copy fails
        """
        try:
            source_blob_client = self._client.get_blob_client(
                container=source_container, blob=source_blob
            )

            if not source_blob_client.exists():
                error_msg = f"Source blob not found: {source_container}/{source_blob}"
                logger.error(error_msg)
                raise BlobNotFoundError(error_msg)

            dest_blob_client = self._client.get_blob_client(
                container=dest_container, blob=dest_blob
            )

            # Start copy operation
            dest_blob_client.start_copy_from_url(source_blob_client.url)

            logger.info(
                f"Blob copied successfully: {source_container}/{source_blob} -> {dest_container}/{dest_blob}"
            )
            return True

        except BlobNotFoundError:
            raise

        except Exception as e:
            error_msg = f"Failed to copy blob {source_container}/{source_blob} to {dest_container}/{dest_blob}: {e}"
            logger.error(error_msg)
            raise BlobStorageError(error_msg)

    def get_blob_url(
        self, container_name: str, blob_name: str, with_sas: bool = False
    ) -> str:
        """
        Get the URL of a blob.

        Args:
            container_name (str): Name of the container
            blob_name (str): Name of the blob
            with_sas (bool): Whether to generate SAS token (not implemented yet)

        Returns:
            str: Blob URL

        Raises:
            BlobStorageError: When URL retrieval fails
        """
        try:
            blob_client = self._client.get_blob_client(
                container=container_name, blob=blob_name
            )

            if with_sas:
                logger.warning("SAS token generation not implemented yet")

            blob_url = blob_client.url
            logger.info(f"Retrieved blob URL: {container_name}/{blob_name}")
            return blob_url

        except Exception as e:
            error_msg = f"Failed to get blob URL {container_name}/{blob_name}: {e}"
            logger.error(error_msg)
            raise BlobStorageError(error_msg)

