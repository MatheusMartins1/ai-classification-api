"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Supabase client service for storage and database operations.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

import os
from typing import Any, Dict, List, Optional

from supabase import Client, create_client

from utils.LoggerConfig import LoggerConfig

logger = LoggerConfig.add_file_logger(
    name="supabase_client",
    filename=None,
    dir_name=None,
    prefix="supabase",
    level_name="INFO",
)


class SupabaseService:
    """
    Service class for Supabase operations.
    Single responsibility: Handle Supabase Storage and Database operations.
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
    ) -> None:
        """
        Initialize Supabase service.

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase anon/service key

        Raises:
            ValueError: When credentials are missing
        """
        self._url = supabase_url or os.getenv("SUPABASE_URL")
        self._key = supabase_key or os.getenv("SUPABASE_SERVICE_KEY")

        if not self._url or not self._key:
            raise ValueError(
                "Supabase credentials not provided. "
                "Set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables"
            )

        self._client: Client = create_client(self._url, self._key)

    @property
    def client(self) -> Client:
        """
        Get Supabase client instance.

        Returns:
            Supabase client
        """
        return self._client

    # Storage Operations

    def upload_file(
        self,
        bucket_name: str,
        file_path: str,
        file_data: bytes,
        content_type: Optional[str] = None,
        if_exists: Optional[str] = "overwrite",
    ) -> str:
        """
        Upload file to Supabase Storage.

        Args:
            bucket_name: Storage bucket name
            file_path: Path/name for the file in storage
            file_data: File bytes to upload
            content_type: MIME type of the file

        Returns:
            Public URL of uploaded file

        Raises:
            Exception: If upload fails
        """
        options = {"content-type": content_type} if content_type else {}

        if if_exists == "overwrite":
            try:
                self.delete_file(bucket_name, file_path)
            except Exception as e:
                logger.error(f"Error deleting file: {e}")
                raise e
        elif if_exists == "skip":
            try:
                if self.get_public_url(bucket_name, file_path):
                    return self.get_public_url(bucket_name, file_path)
            except Exception as e:
                logger.error(f"Error checking if file exists: {e}")
                raise e

        try:
            response = self._client.storage.from_(bucket_name).upload(
                file_path, file_data, file_options=options
            )
            return self.get_public_url(bucket_name, file_path)
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise e

    def download_file(self, bucket_name: str, file_path: str) -> bytes:
        """
        Download file from Supabase Storage.

        Args:
            bucket_name: Storage bucket name
            file_path: Path/name of the file in storage

        Returns:
            File bytes

        Raises:
            Exception: If download fails
        """
        response = self._client.storage.from_(bucket_name).download(file_path)
        return response

    def delete_file(self, bucket_name: str, file_path: str) -> None:
        """
        Delete file from Supabase Storage.

        Args:
            bucket_name: Storage bucket name
            file_path: Path/name of the file in storage

        Raises:
            Exception: If deletion fails
        """
        self._client.storage.from_(bucket_name).remove([file_path])

    def list_files(self, bucket_name: str, folder_path: str = "") -> List[Dict]:
        """
        List files in Supabase Storage bucket.

        Args:
            bucket_name: Storage bucket name
            folder_path: Folder path to list files from

        Returns:
            List of file metadata dictionaries

        Raises:
            Exception: If listing fails
        """
        response = self._client.storage.from_(bucket_name).list(folder_path)
        return response

    def get_public_url(self, bucket_name: str, file_path: str) -> str:
        """
        Get public URL for a file in Supabase Storage.

        Args:
            bucket_name: Storage bucket name
            file_path: Path/name of the file in storage

        Returns:
            Public URL string
        """
        response = self._client.storage.from_(bucket_name).get_public_url(file_path)
        return response

    # Database Operations

    def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert data into Supabase table.

        Args:
            table: Table name
            data: Dictionary with data to insert

        Returns:
            Inserted record

        Raises:
            Exception: If insertion fails
        """
        response = self._client.table(table).insert(data).execute()
        return response.data[0] if response.data else {}

    def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Select data from Supabase table.

        Args:
            table: Table name
            columns: Columns to select (default: "*")
            filters: Dictionary with filter conditions

        Returns:
            List of records

        Raises:
            Exception: If query fails
        """
        query = self._client.table(table).select(columns)

        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        response = query.execute()
        return response.data

    def update(
        self, table: str, data: Dict[str, Any], filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Update data in Supabase table.

        Args:
            table: Table name
            data: Dictionary with data to update
            filters: Dictionary with filter conditions

        Returns:
            Updated records

        Raises:
            Exception: If update fails
        """
        query = self._client.table(table).update(data)

        for key, value in filters.items():
            query = query.eq(key, value)

        response = query.execute()
        return response.data

    def delete(self, table: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Delete data from Supabase table.

        Args:
            table: Table name
            filters: Dictionary with filter conditions

        Returns:
            Deleted records

        Raises:
            Exception: If deletion fails
        """
        query = self._client.table(table).delete()

        for key, value in filters.items():
            query = query.eq(key, value)

        response = query.execute()
        return response.data

    def upsert(
        self, table: str, data: Dict[str, Any], on_conflict: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upsert (insert or update) data in Supabase table.

        Args:
            table: Table name
            data: Dictionary with data to upsert
            on_conflict: Column name for conflict resolution

        Returns:
            Upserted record

        Raises:
            Exception: If upsert fails
        """
        options = {"on_conflict": on_conflict} if on_conflict else {}
        response = self._client.table(table).upsert(data, **options).execute()
        return response.data[0] if response.data else {}
