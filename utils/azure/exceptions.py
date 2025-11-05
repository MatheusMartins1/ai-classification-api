"""
@fileoverview Azure Custom Exceptions
@description Application-specific exception classes for Azure services
@author Matheus Martins
@created 2025-11-04
@lastmodified 2025-11-04
"""


class AzureError(Exception):
    """Base exception for Azure-related errors."""

    pass


class AzureConnectionError(AzureError):
    """Raised when Azure connection fails."""

    pass


class AzureAuthenticationError(AzureError):
    """Raised when Azure authentication fails."""

    pass


class BlobStorageError(AzureError):
    """Base exception for Blob Storage-related errors."""

    pass


class BlobNotFoundError(BlobStorageError):
    """Raised when a requested blob is not found."""

    pass


class BlobUploadError(BlobStorageError):
    """Raised when blob upload fails."""

    pass


class BlobDownloadError(BlobStorageError):
    """Raised when blob download fails."""

    pass


class BlobDeleteError(BlobStorageError):
    """Raised when blob deletion fails."""

    pass


class ContainerNotFoundError(BlobStorageError):
    """Raised when a requested container is not found."""

    pass


class ContainerCreationError(BlobStorageError):
    """Raised when container creation fails."""

    pass

