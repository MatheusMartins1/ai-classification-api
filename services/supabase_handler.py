"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Service handler for Supabase storage operations with thermal image data.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

import asyncio
import os
import shutil
from typing import Any, Dict, List

from utils.LoggerConfig import LoggerConfig
from utils.supabase_client import SupabaseService

logger = LoggerConfig.add_file_logger(
    name="supabase_handler",
    filename=None,
    dir_name=None,
    prefix="supabase_handler",
    level_name="INFO",
)


class SupabaseStorageHandler:
    """
    Handler class for Supabase storage operations.
    Single responsibility: Manage thermal image file uploads to Supabase storage.
    """

    def __init__(self, bucket_name: str = "imagem") -> None:
        """
        Initialize Supabase storage handler.

        Args:
            bucket_name: Default bucket name for storage operations
        """
        self.supabase_service = SupabaseService()
        self.bucket_name = bucket_name

    async def send_data_to_storage(self, response_data: Dict[str, Any]) -> bool:
        """
        Save thermal image files to Supabase storage.

        Args:
            response_data: Dictionary containing IR images and user info

        Returns:
            True if all uploads succeed, False otherwise

        Raises:
            Exception: If upload fails
        """
        files_to_upload = ["image_saved_ir_filename", "image_saved_real_filename"]
        task_success = []

        for index, image in enumerate(response_data["ir_images"]):
            storage_info = image.get("metadata", {}).get("storage_info", {})
            image_path = os.path.join(storage_info.get("image_folder", ""))

            # Upload IR and Real images
            for file in files_to_upload:
                success = await self._upload_image_file(
                    response_data=response_data,
                    storage_info=storage_info,
                    image_path=image_path,
                    file_key=file,
                    content_type=image["content_type"],
                )
                task_success.append(success)

            # Upload temperature CSV
            success = await self._upload_temperature_file(
                response_data=response_data,
                storage_info=storage_info,
                image_path=image_path,
                file_extension="csv",
            )
            task_success.append(success)

            # Upload temperature JSON
            success = await self._upload_temperature_file(
                response_data=response_data,
                storage_info=storage_info,
                image_path=image_path,
                file_extension="json",
            )
            task_success.append(success)

            # Upload metadata JSON
            success = await self._upload_metadata_file(
                response_data=response_data,
                storage_info=storage_info,
                image_path=image_path,
            )
            task_success.append(success)

        if all(task_success):
            # Remove temp folder after successful upload
            shutil.rmtree(image_path)
            logger.info(f"Successfully uploaded all files and cleaned temp folder: {image_path}")
            return True
        else:
            logger.error("Some uploads failed. Temp folder not removed.")
            return False

    async def _upload_image_file(
        self,
        response_data: Dict[str, Any],
        storage_info: Dict[str, str],
        image_path: str,
        file_key: str,
        content_type: str,
    ) -> bool:
        """
        Upload a single image file to storage.

        Args:
            response_data: Response data containing user info
            storage_info: Storage information dictionary
            image_path: Local path to the image
            file_key: Key to get filename from storage_info
            content_type: MIME type of the file

        Returns:
            True if upload succeeds, False otherwise
        """
        try:
            file_path = self._build_storage_path(
                response_data=response_data,
                storage_info=storage_info,
                filename=storage_info.get(file_key, ""),
            )

            file_data = open(
                os.path.join(image_path, storage_info.get(file_key, "")),
                "rb",
            ).read()

            await asyncio.to_thread(
                self.supabase_service.upload_file,
                bucket_name=self.bucket_name,
                file_path=file_path,
                file_data=file_data,
                content_type=content_type,
                if_exists="overwrite",
            )
            logger.info(f"Successfully uploaded: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error uploading file {file_key}: {e}")
            return False

    async def _upload_temperature_file(
        self,
        response_data: Dict[str, Any],
        storage_info: Dict[str, str],
        image_path: str,
        file_extension: str,
    ) -> bool:
        """
        Upload temperature data file (CSV or JSON) to storage.

        Args:
            response_data: Response data containing user info
            storage_info: Storage information dictionary
            image_path: Local path to the file
            file_extension: File extension (csv or json)

        Returns:
            True if upload succeeds, False otherwise
        """
        try:
            file_name = f"{storage_info.get('image_filename', '')}_temperature.{file_extension}"
            file_path = self._build_storage_path(
                response_data=response_data,
                storage_info=storage_info,
                filename=file_name,
            )

            file_data = open(os.path.join(image_path, file_name), "rb").read()

            await asyncio.to_thread(
                self.supabase_service.upload_file,
                bucket_name=self.bucket_name,
                file_path=file_path,
                file_data=file_data,
                if_exists="overwrite",
            )
            logger.info(f"Successfully uploaded: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error uploading temperature.{file_extension}: {e}")
            return False

    async def _upload_metadata_file(
        self,
        response_data: Dict[str, Any],
        storage_info: Dict[str, str],
        image_path: str,
    ) -> bool:
        """
        Upload metadata JSON file to storage.

        Args:
            response_data: Response data containing user info
            storage_info: Storage information dictionary
            image_path: Local path to the file

        Returns:
            True if upload succeeds, False otherwise
        """
        try:
            file_name = f"{storage_info.get('image_filename', '')}_metadata.json"
            file_path = self._build_storage_path(
                response_data=response_data,
                storage_info=storage_info,
                filename=file_name,
            )

            file_data = open(os.path.join(image_path, file_name), "rb").read()

            await asyncio.to_thread(
                self.supabase_service.upload_file,
                bucket_name=self.bucket_name,
                file_path=file_path,
                file_data=file_data,
                if_exists="overwrite",
            )
            logger.info(f"Successfully uploaded: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error uploading metadata.json: {e}")
            return False

    def _build_storage_path(
        self,
        response_data: Dict[str, Any],
        storage_info: Dict[str, str],
        filename: str,
    ) -> str:
        """
        Build storage path for file upload.

        Args:
            response_data: Response data containing user info
            storage_info: Storage information dictionary
            filename: Name of the file

        Returns:
            Storage path string
        """
        return "/".join(
            [
                "companies",
                response_data.get("user_info", {}).get("company_id", ""),
                storage_info.get("image_filename", ""),
                filename,
            ]
        )

