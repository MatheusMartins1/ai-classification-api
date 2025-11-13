"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Service for building ThermalImageData objects with temperature conversion.
Based on flyr library structure.
Reference: https://bitbucket.org/nimmerwoner/flyr/src/master/flyr/flyr.py
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

import os
import uuid
from typing import Any, Dict, List, Optional

import numpy as np  # type: ignore
import pandas as pd  # type: ignore

from models.thermal_data import (
    CameraMetadata,
    ExifToolMetadata,
    FlyrMetadata,
    Measurement,
    PaletteInfo,
    PipInfo,
    StorageInfo,
    TemperatureData,
    ThermalImageData,
)
from services.measurement_extractor import MeasurementExtractor
from utils import temperature_calculations
from utils.LoggerConfig import LoggerConfig
from utils.object_handler import extract_all_attributes

logger = LoggerConfig.add_file_logger(
    name="thermal_data_builder",
    filename=None,
    dir_name=None,
    prefix="thermal_builder",
    level_name="INFO",
)


class ThermalDataBuilder:
    """
    Service class for building ThermalImageData objects.
    Single responsibility: Build and convert thermal data to standard format.
    """

    def __init__(self, temp_folder: str = "temp"):
        """
        Initialize ThermalDataBuilder.

        Args:
            temp_folder: Base folder for temporary files
        """
        self.temp_folder = temp_folder
        self.measurement_extractor = MeasurementExtractor()

    def build_thermal_image_data(
        self,
        thermogram: Any,
        image_name: str,
        save_files: bool = True,
        form_data: Optional[dict] = None,
        exiftool_metadata: Optional[ExifToolMetadata] = None,
    ) -> ThermalImageData:
        """
        Build complete ThermalImageData object from thermogram.

        Args:
            thermogram: Thermogram object from flyr
            image_name: Name of the thermal image file
            save_files: Whether to save temperature files (CSV, JSON)
            form_data: Form data containing tag and other metadata
            exiftool_metadata: Optional ExifToolMetadata object

        Returns:
            Complete ThermalImageData object with all metadata and conversions
        """
        logger.info(f"Building ThermalImageData for: {image_name}")

        # Create storage info
        form_data = form_data or {}
        storage_info = self._create_storage_info(image_name, form_data)

        # Build metadata with temperature conversion
        flyr_metadata = self.build_flyr_metadata(thermogram)
        camera_metadata = self.build_camera_metadata(thermogram)
        pip_info = self.build_pip_info(thermogram)
        palette_info = self.build_palette_info(thermogram)

        # Get temperature unit for conversions
        temperature_unit_original = (
            flyr_metadata.temperature_unit_original if flyr_metadata else "K"
        )
        logger.info(f"Temperature unit original: {temperature_unit_original}")

        # Extract and process temperature data
        temperature_data = self._build_temperature_data(
            thermogram, storage_info, save_files
        )

        # Extract measurements with temperature statistics
        measurements = self._build_measurements(thermogram, temperature_data)

        # Build complete thermal image data
        thermal_data = ThermalImageData(
            storage_info=storage_info,
            flyr_metadata=flyr_metadata,
            camera_metadata=camera_metadata,
            exiftool_metadata=exiftool_metadata,
            temperature_data=temperature_data,
            measurements=measurements,
            pip_info=pip_info,
            palette_info=palette_info,
        )

        logger.info(f"Successfully built ThermalImageData for: {image_name}")
        return thermal_data

    def build_thermal_image_data_as_dict(
        self,
        thermogram: Any,
        image_name: str,
        save_files: bool = True,
        form_data: Optional[dict] = None,
        exiftool_metadata: Optional[ExifToolMetadata] = None,
    ) -> Dict[str, Any]:
        """
        Build complete thermal image data and return as dictionary.

        Args:
            thermogram: Thermogram object from flyr
            image_name: Name of the thermal image file
            save_files: Whether to save temperature files
            form_data: Form data containing tag and other metadata
            exiftool_metadata: Optional ExifToolMetadata object

        Returns:
            Dictionary with all thermal image data
        """
        thermal_data = self.build_thermal_image_data(
            thermogram, image_name, save_files, form_data, exiftool_metadata
        )
        return thermal_data.model_dump(exclude_none=True)

    def _create_storage_info(self, image_name: str, form_data: dict) -> StorageInfo:
        """
        Create StorageInfo from image name.

        Args:
            image_name: Name of the image file
            tag: Tag identifier for the image

        Returns:
            StorageInfo object
        """
        database_id = str(uuid.uuid4())
        tag = form_data.get("tag", "")
        created_date = form_data.get("data_criacao", "")
        id_inspecao = form_data.get("id_inspecao", "")
        empresa_site = form_data.get("empresa_site", "")
        localizacao_1 = form_data.get("localizacao_1", "")
        localizacao_2 = form_data.get("localizacao_2", "")
        divisao = form_data.get("divisao", "")
        setor = form_data.get("setor", "")
        user_id = form_data.get("criado_por", "")
        company_id = form_data.get("company_id", "")
        image_name_parts = image_name.split(".")
        image_filename = image_name_parts[0]
        image_extension = image_name_parts[1] if len(image_name_parts) > 1 else "jpg"
        image_folder = os.path.join(self.temp_folder, image_filename)

        return StorageInfo(
            database_id=database_id,
            id_inspecao=id_inspecao,
            tag=tag,
            empresa_site=empresa_site,
            localizacao_1=localizacao_1,
            localizacao_2=localizacao_2,
            divisao=divisao,
            setor=setor,
            user_id=user_id,
            company_id=company_id,
            created_date=created_date,
            image_filename=image_filename,
            image_folder=image_folder,
            image_extension=image_extension,
            image_saved_ir_filename=f"{image_filename}_IR.{image_extension}",
            image_saved_real_filename=f"{image_filename}_REAL.{image_extension}",
        )

    def _build_temperature_data(
        self, thermogram: Any, storage_info: StorageInfo, save_files: bool
    ) -> Optional[TemperatureData]:
        """
        Build TemperatureData from thermogram.

        Args:
            thermogram: Thermogram object from flyr
            storage_info: Storage information
            save_files: Whether to save temperature files

        Returns:
            TemperatureData object or None
        """
        try:
            if not hasattr(thermogram, "celsius"):
                logger.warning("Thermogram has no celsius attribute")
                return None

            celsius_array = thermogram.celsius

            # Convert to list for JSON serialization
            celsius_list = (
                celsius_array.tolist()
                if hasattr(celsius_array, "tolist")
                else celsius_array
            )

            # Calculate statistics
            celsius_np = np.array(celsius_array)
            min_temp = temperature_calculations.get_min_from_temperature_array(
                celsius_np
            )
            max_temp = temperature_calculations.get_max_from_temperature_array(
                celsius_np
            )
            avg_temp = temperature_calculations.get_average_from_temperature_array(
                celsius_np
            )
            median_temp = temperature_calculations.get_median_from_temperature_array(
                celsius_np
            )
            delta_t = temperature_calculations.generate_delta(min_temp, max_temp)

            # Save temperature files if requested
            if save_files:
                self._save_temperature_files(celsius_array, storage_info)

            return TemperatureData(
                celsius=celsius_list,
                min_temperature=min_temp,
                max_temperature=max_temp,
                avg_temperature=avg_temp,
                median_temperature=median_temp,
                delta_t=delta_t,
            )

        except Exception as e:
            logger.error(f"Error building TemperatureData: {e}")
            return None

    def _build_measurements(
        self, thermogram: Any, temperature_data: Optional[TemperatureData]
    ) -> Optional[List[Measurement]]:
        """
        Build measurements from thermogram.

        Args:
            thermogram: Thermogram object from flyr
            temperature_data: Temperature data for extracting region temperatures

        Returns:
            List of Measurement objects or None
        """
        try:
            celsius_array = None
            if temperature_data and hasattr(thermogram, "celsius"):
                celsius_array = thermogram.celsius

            measurements = self.measurement_extractor.extract_measurements(
                thermogram, celsius_array
            )

            return measurements if measurements else None

        except Exception as e:
            logger.error(f"Error building measurements: {e}")
            return None

    def _save_temperature_files(
        self, celsius_array: np.ndarray, storage_info: StorageInfo
    ) -> None:
        """
        Save temperature data to CSV and JSON files.

        Args:
            celsius_array: Temperature array
            storage_info: Storage information
        """
        try:
            # Create folder if not exists
            os.makedirs(storage_info.image_folder, exist_ok=True)

            # Save as CSV
            temperature_df = pd.DataFrame(celsius_array)
            csv_path = os.path.join(
                storage_info.image_folder,
                f"{storage_info.image_filename}_temperature.csv",
            )
            temperature_df.to_csv(csv_path, index=False)

            # Save as JSON
            json_path = os.path.join(
                storage_info.image_folder,
                f"{storage_info.image_filename}_temperature.json",
            )
            temperature_df.to_json(json_path, orient="records")

            logger.info(f"Saved temperature files to: {storage_info.image_folder}")

        except Exception as e:
            logger.error(f"Error saving temperature files: {e}")

    def build_flyr_metadata(
        self, thermogram: Any, temperature_unit_original: str = "K"
    ) -> Optional[FlyrMetadata]:
        """
        Build FlyrMetadata from thermogram with temperature conversion.

        Args:
            thermogram: Thermogram object from flyr
            temperature_unit_original: Original temperature unit from thermogram

        Returns:
            FlyrMetadata object with temperatures in Celsius
        """
        try:
            # Extract all metadata attributes
            metadata_dict = thermogram.metadata

            if not isinstance(metadata_dict, dict):
                logger.warning("metadata_dict is not a dict")
                return None

            # Detect original temperature unit
            detected_unit = self._detect_temperature_unit(metadata_dict)
            if detected_unit:
                temperature_unit_original = detected_unit

            logger.info(f"Original temperature unit: {temperature_unit_original}")

            # Convert temperature fields to Celsius
            flyr_metadata = FlyrMetadata(
                temperature_unit="C",
                temperature_unit_original=temperature_unit_original,
                # Environmental parameters (with temperature conversion)
                emissivity=metadata_dict.get("emissivity"),
                object_distance=metadata_dict.get("object_distance"),
                atmospheric_temperature=self._convert_to_celsius(
                    metadata_dict.get("atmospheric_temperature"),
                    temperature_unit_original,
                ),
                ir_window_temperature=self._convert_to_celsius(
                    metadata_dict.get("ir_window_temperature"),
                    temperature_unit_original,
                ),
                ir_window_transmission=metadata_dict.get("ir_window_transmission"),
                reflected_apparent_temperature=self._convert_to_celsius(
                    metadata_dict.get("reflected_apparent_temperature"),
                    temperature_unit_original,
                ),
                relative_humidity=metadata_dict.get("relative_humidity"),
                # Planck constants
                planck_r1=metadata_dict.get("planck_r1"),
                planck_b=metadata_dict.get("planck_b"),
                planck_f=metadata_dict.get("planck_f"),
                planck_o=metadata_dict.get("planck_o"),
                atmospheric_trans_alpha1=metadata_dict.get("atmospheric_trans_alpha1"),
                atmospheric_trans_alpha2=metadata_dict.get("atmospheric_trans_alpha2"),
                atmospheric_trans_beta1=metadata_dict.get("atmospheric_trans_beta1"),
                atmospheric_trans_beta2=metadata_dict.get("atmospheric_trans_beta2"),
                atmospheric_trans_x=metadata_dict.get("atmospheric_trans_x"),
                # Raw value ranges
                raw_value_range_min=metadata_dict.get("raw_value_range_min"),
                raw_value_range_max=metadata_dict.get("raw_value_range_max"),
                raw_value_median=metadata_dict.get("raw_value_median"),
                raw_value_range=metadata_dict.get("raw_value_range"),
                # Camera temperature ranges
                camera_temperature_range_max=metadata_dict.get(
                    "camera_temperature_range_max"
                ),
                camera_temperature_range_min=metadata_dict.get(
                    "camera_temperature_range_min"
                ),
                # Complete raw metadata
                raw_metadata=metadata_dict,
            )

            return flyr_metadata

        except Exception as e:
            logger.error(f"Error building FlyrMetadata: {e}")
            return None

    def build_camera_metadata(self, thermogram: Any) -> Optional[CameraMetadata]:
        """
        Build CameraMetadata from thermogram.

        Args:
            thermogram: Thermogram object from flyr

        Returns:
            CameraMetadata object
        """
        try:
            if not hasattr(thermogram, "camera_metadata"):
                return None

            camera_dict = extract_all_attributes(
                thermogram.camera_metadata, "camera_metadata"
            )

            if not isinstance(camera_dict, dict):
                return None

            # Extract data field if it exists (nested structure)
            data_dict = camera_dict.get("data", {})
            if isinstance(data_dict, dict):
                # Merge data dict with camera dict
                camera_dict.update(data_dict)

            return CameraMetadata(
                resolution_unit=camera_dict.get("resolution_unit"),
                exif_offset=camera_dict.get("exif_offset"),
                make=camera_dict.get("make"),
                model=camera_dict.get("model"),
                serial_number=camera_dict.get("serial_number"),
                date_time=camera_dict.get("date_time"),
                gps_data=camera_dict.get("gps_data"),
                raw_camera_metadata=camera_dict,
            )

        except Exception as e:
            logger.warning(f"Error building CameraMetadata: {e}")
            return None

    def build_pip_info(self, thermogram: Any) -> Optional[PipInfo]:
        """
        Build PipInfo from thermogram.

        Args:
            thermogram: Thermogram object from flyr

        Returns:
            PipInfo object or None
        """
        try:
            if not hasattr(thermogram, "pip_info"):
                return None

            pip_dict = thermogram.pip_info

            if not isinstance(pip_dict, dict):
                return None

            return PipInfo(
                pip_x=pip_dict.get("x"),
                pip_y=pip_dict.get("y"),
                pip_width=pip_dict.get("width"),
                pip_height=pip_dict.get("height"),
            )

        except Exception as e:
            logger.warning(f"Error building PipInfo: {e}")
            return None

    def build_palette_info(self, thermogram: Any) -> Optional[PaletteInfo]:
        """
        Build PaletteInfo from thermogram.

        Args:
            thermogram: Thermogram object from flyr

        Returns:
            PaletteInfo object or None
        """
        try:
            if not hasattr(thermogram, "palette"):
                return None

            palette_raw = thermogram.palette

            # If it's an object, extract attributes
            if not isinstance(palette_raw, dict):
                palette_dict = extract_all_attributes(palette_raw, "palette_info")
            else:
                palette_dict = palette_raw

            if not isinstance(palette_dict, dict):
                return None

            # Convert RGB values to list of tuples if it's a list
            rgb_values = palette_dict.get("rgb_values") or palette_dict.get("rgbs")
            if rgb_values and isinstance(rgb_values, list):
                # Ensure each item is a tuple
                rgb_values = [tuple(rgb) if isinstance(rgb, (list, tuple)) else rgb for rgb in rgb_values]  # type: ignore

            # Convert YCbCr values to list of tuples if available
            yccs = palette_dict.get("yccs")
            if yccs and isinstance(yccs, list):
                yccs = [tuple(ycc) if isinstance(ycc, (list, tuple)) else ycc for ycc in yccs]  # type: ignore

            # Helper function to safely convert to tuple
            def safe_tuple(value):
                if value and isinstance(value, (list, tuple)):
                    return tuple(value)
                return None

            return PaletteInfo(
                above_color=safe_tuple(palette_dict.get("above_color")),
                below_color=safe_tuple(palette_dict.get("below_color")),
                overflow_color=safe_tuple(palette_dict.get("overflow_color")),
                underflow_color=safe_tuple(palette_dict.get("underflow_color")),
                isotherm1_color=safe_tuple(palette_dict.get("isotherm1_color")),
                isotherm2_color=safe_tuple(palette_dict.get("isotherm2_color")),
                method=palette_dict.get("method"),
                name=palette_dict.get("name"),
                num_colors=palette_dict.get("num_colors"),
                stretch=palette_dict.get("stretch"),
                file_name=palette_dict.get("file_name"),
                path=palette_dict.get("path"),
                rgb_values=rgb_values,
                yccs=yccs,
            )

        except Exception as e:
            logger.warning(f"Error building PaletteInfo: {e}")
            return None

    def _detect_temperature_unit(self, metadata_dict: dict) -> Optional[str]:
        """
        Detect temperature unit from metadata.

        Args:
            metadata_dict: Metadata dictionary

        Returns:
            Temperature unit string or None
        """
        # Check for temperature_unit field
        if "temperature_unit" in metadata_dict:
            return str(metadata_dict["temperature_unit"])

        # Check for unit field
        if "unit" in metadata_dict:
            return str(metadata_dict["unit"])

        # Flyr typically uses Kelvin by default
        return "K"

    def _convert_to_celsius(
        self, value: Optional[float], original_unit: str
    ) -> Optional[float]:
        """
        Convert temperature value to Celsius.

        Args:
            value: Temperature value
            original_unit: Original temperature unit

        Returns:
            Temperature in Celsius or None
        """
        if value is None:
            return None

        try:
            return temperature_calculations.convert_temperature_value_to_celsius(
                value, original_unit
            )
        except Exception as e:
            logger.warning(
                f"Error converting temperature {value} from {original_unit}: {e}"
            )
            return value  # Return original value if conversion fails
