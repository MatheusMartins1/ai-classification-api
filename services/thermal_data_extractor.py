"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Service for extracting thermal data from FLIR images using flyr and ExifTool.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

import json
import os
import subprocess
from typing import Any, Dict, Optional

import flyr
import numpy as np
import pandas as pd
from PIL import Image

from models.thermal_data import (
    CameraMetadata,
    ExifToolMetadata,
    FlyrMetadata,
    PipInfo,
    StorageInfo,
    TemperatureData,
    ThermalImageData,
)
from utils.LoggerConfig import LoggerConfig
from utils.object_handler import extract_all_attributes

logger = LoggerConfig.add_file_logger(
    name="thermal_data_extractor",
    filename=None,
    dir_name=None,
    prefix="thermal_extractor",
    level_name="INFO",
)


class ThermalDataExtractor:
    """
    Service class for extracting thermal data from FLIR images.
    Combines data from flyr library and ExifTool.
    Single responsibility: Extract and structure thermal image data.
    """

    def __init__(self, temp_folder: str = "temp") -> None:
        """
        Initialize thermal data extractor.

        Args:
            temp_folder: Base folder for temporary file storage
        """
        self.temp_folder = temp_folder

    def extract_thermal_data(self, image_name: str) -> ThermalImageData:
        """
        Extract complete thermal data from FLIR image.

        Args:
            image_name: Name of the FLIR image file

        Returns:
            ThermalImageData object with all extracted data

        Raises:
            Exception: If extraction fails
        """
        # Setup storage paths
        storage_info = self._create_storage_info(image_name)
        image_folder = storage_info.image_folder
        os.makedirs(image_folder, exist_ok=True)

        # Extract data using flyr
        logger.info(f"Extracting thermal data from: {image_name}")
        thermogram = self._load_thermogram(storage_info)

        # Extract all data
        flyr_metadata = self._extract_flyr_metadata(thermogram)
        camera_metadata = self._extract_camera_metadata(thermogram)
        temperature_data = self._extract_temperature_data(thermogram, storage_info)
        pip_info = self._extract_pip_info(thermogram)

        # Save optical image
        self._save_optical_image(thermogram, storage_info)

        # Extract ExifTool metadata
        exiftool_metadata = self._extract_exiftool_metadata(storage_info)

        # Create complete thermal image data
        thermal_data = ThermalImageData(
            storage_info=storage_info,
            flyr_metadata=flyr_metadata,
            camera_metadata=camera_metadata,
            exiftool_metadata=exiftool_metadata,
            temperature_data=temperature_data,
            pip_info=pip_info,
        )

        # Save metadata JSON
        self._save_metadata_json(thermal_data, storage_info)

        logger.info(f"Successfully extracted thermal data from: {image_name}")
        return thermal_data

    def _create_storage_info(self, image_name: str) -> StorageInfo:
        """
        Create storage information structure.

        Args:
            image_name: Name of the image file

        Returns:
            StorageInfo object
        """
        image_name_parts = image_name.split(".")
        image_filename = image_name_parts[0]
        image_extension = image_name_parts[1] if len(image_name_parts) > 1 else "jpg"
        image_folder = os.path.join(self.temp_folder, image_filename)

        return StorageInfo(
            image_filename=image_filename,
            image_folder=image_folder,
            image_extension=image_extension,
            image_saved_ir_filename=f"{image_filename}_IR.{image_extension}",
            image_saved_real_filename=f"{image_filename}_REAL.{image_extension}",
        )

    def _load_thermogram(self, storage_info: StorageInfo) -> Any:
        """
        Load thermogram using flyr library.

        Args:
            storage_info: Storage information

        Returns:
            Thermogram object from flyr

        Raises:
            Exception: If loading fails
        """
        image_path = os.path.join(
            storage_info.image_folder,
            storage_info.image_saved_ir_filename,
        )

        try:
            thermogram = flyr.unpack(image_path)
            return thermogram
        except Exception as e:
            logger.error(f"Error loading thermogram: {e}")
            raise e

    def _extract_flyr_metadata(self, thermogram: Any) -> Optional[FlyrMetadata]:
        """
        Extract metadata from flyr thermogram.

        Args:
            thermogram: Thermogram object from flyr

        Returns:
            FlyrMetadata object or None if extraction fails
        """
        try:
            metadata_dict = extract_all_attributes(thermogram.metadata, "metadata")

            return FlyrMetadata(
                emissivity=metadata_dict.get("emissivity"),
                reflected_apparent_temperature=metadata_dict.get(
                    "reflected_apparent_temperature"
                ),
                atmospheric_temperature=metadata_dict.get("atmospheric_temperature"),
                relative_humidity=metadata_dict.get("relative_humidity"),
                ir_window_temperature=metadata_dict.get("ir_window_temperature"),
                ir_window_transmission=metadata_dict.get("ir_window_transmission"),
                temperature_range=metadata_dict.get("temperature_range"),
                object_distance=metadata_dict.get("object_distance"),
                camera_model=metadata_dict.get("camera_model"),
                camera_serial_number=metadata_dict.get("camera_serial_number"),
                lens_model=metadata_dict.get("lens_model"),
                filter_model=metadata_dict.get("filter_model"),
                date_time_original=metadata_dict.get("date_time_original"),
                raw_metadata=metadata_dict,
            )
        except Exception as e:
            logger.warning(f"Error extracting flyr metadata: {e}")
            return None

    def _extract_camera_metadata(self, thermogram: Any) -> Optional[CameraMetadata]:
        """
        Extract camera metadata from thermogram.

        Args:
            thermogram: Thermogram object from flyr

        Returns:
            CameraMetadata object or None if extraction fails
        """
        try:
            camera_dict = extract_all_attributes(
                thermogram.camera_metadata, "camera_metadata"
            )

            return CameraMetadata(
                camera_manufacturer=camera_dict.get("camera_manufacturer"),
                camera_model=camera_dict.get("camera_model"),
                camera_serial_number=camera_dict.get("camera_serial_number"),
                lens_model=camera_dict.get("lens_model"),
                lens_serial_number=camera_dict.get("lens_serial_number"),
                raw_camera_metadata=camera_dict,
            )
        except Exception as e:
            logger.warning(f"Error extracting camera metadata: {e}")
            return None

    def _extract_temperature_data(
        self, thermogram: Any, storage_info: StorageInfo
    ) -> Optional[TemperatureData]:
        """
        Extract temperature matrix data from thermogram.

        Args:
            thermogram: Thermogram object from flyr
            storage_info: Storage information

        Returns:
            TemperatureData object or None if extraction fails
        """
        try:
            celsius_array = thermogram.celsius
            temperature_list = celsius_array.tolist()

            # Calculate statistics
            min_temp = float(np.min(celsius_array))
            max_temp = float(np.max(celsius_array))
            avg_temp = float(np.mean(celsius_array))
            median_temp = float(np.median(celsius_array))

            # Save temperature data to files
            temperature_df = pd.DataFrame(celsius_array)
            temperature_df.to_csv(
                os.path.join(
                    storage_info.image_folder,
                    f"{storage_info.image_filename}_temperature.csv",
                ),
                index=False,
            )
            temperature_df.to_json(
                os.path.join(
                    storage_info.image_folder,
                    f"{storage_info.image_filename}_temperature.json",
                ),
                orient="records",
            )

            return TemperatureData(
                celsius=temperature_list,
                min_temperature=min_temp,
                max_temperature=max_temp,
                avg_temperature=avg_temp,
                median_temperature=median_temp,
            )
        except Exception as e:
            logger.warning(f"Error extracting temperature data: {e}")
            return None

    def _extract_pip_info(self, thermogram: Any) -> Optional[PipInfo]:
        """
        Extract Picture-in-Picture information from thermogram.

        Args:
            thermogram: Thermogram object from flyr

        Returns:
            PipInfo object or None if not available
        """
        try:
            if hasattr(thermogram, "pip_info"):
                pip_dict = extract_all_attributes(thermogram.pip_info, "pip_info")
                return PipInfo(
                    pip_x=pip_dict.get("x"),
                    pip_y=pip_dict.get("y"),
                    pip_width=pip_dict.get("width"),
                    pip_height=pip_dict.get("height"),
                )
        except Exception as e:
            logger.warning(f"Error extracting PIP info: {e}")

        return None

    def _save_optical_image(
        self, thermogram: Any, storage_info: StorageInfo
    ) -> None:
        """
        Save optical image from thermogram.

        Args:
            thermogram: Thermogram object from flyr
            storage_info: Storage information
        """
        try:
            optical_path = os.path.join(
                storage_info.image_folder,
                f"{storage_info.image_filename}_REAL.jpg",
            )
            thermogram.optical_pil.save(optical_path)
            logger.info(f"Saved optical image: {optical_path}")
        except Exception as e:
            logger.error(f"Error saving optical image: {e}")

    def _extract_exiftool_metadata(
        self, storage_info: StorageInfo
    ) -> Optional[ExifToolMetadata]:
        """
        Extract metadata using ExifTool.

        Args:
            storage_info: Storage information

        Returns:
            ExifToolMetadata object or None if extraction fails
        """
        try:
            image_path = os.path.join(
                storage_info.image_folder,
                storage_info.image_saved_ir_filename,
            )

            # Run exiftool command
            result = subprocess.run(
                ["exiftool", "-j", image_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                logger.warning(f"ExifTool failed: {result.stderr}")
                return None

            # Parse JSON output
            exif_data = json.loads(result.stdout)[0]

            return ExifToolMetadata(
                file_size=exif_data.get("FileSize"),
                file_type=exif_data.get("FileType"),
                mime_type=exif_data.get("MIMEType"),
                image_width=exif_data.get("ImageWidth"),
                image_height=exif_data.get("ImageHeight"),
                gps_latitude=exif_data.get("GPSLatitude"),
                gps_longitude=exif_data.get("GPSLongitude"),
                gps_altitude=exif_data.get("GPSAltitude"),
                create_date=exif_data.get("CreateDate"),
                modify_date=exif_data.get("ModifyDate"),
                software=exif_data.get("Software"),
                raw_exif_metadata=exif_data,
            )
        except FileNotFoundError:
            logger.warning("ExifTool not found. Install with: apt-get install exiftool")
            return None
        except Exception as e:
            logger.warning(f"Error extracting ExifTool metadata: {e}")
            return None

    def _save_metadata_json(
        self, thermal_data: ThermalImageData, storage_info: StorageInfo
    ) -> None:
        """
        Save complete metadata to JSON file.

        Args:
            thermal_data: Complete thermal image data
            storage_info: Storage information
        """
        try:
            json_filename = os.path.join(
                storage_info.image_folder,
                f"{storage_info.image_filename}_metadata.json",
            )

            # Convert to dict and save
            metadata_dict = thermal_data.model_dump(exclude_none=True)

            with open(json_filename, "w", encoding="utf-8") as json_file:
                json.dump(metadata_dict, json_file, indent=2, ensure_ascii=False)

            logger.info(f"Saved metadata JSON: {json_filename}")
        except Exception as e:
            logger.error(f"Error saving metadata JSON: {e}")

    def create_response_dict(self, thermal_data: ThermalImageData) -> Dict[str, Any]:
        """
        Create response dictionary from thermal data.

        Args:
            thermal_data: Complete thermal image data

        Returns:
            Response dictionary
        """
        return {
            "success": True,
            "message": "Metadata extracted successfully",
            "metadata": thermal_data.model_dump(exclude_none=True),
        }

