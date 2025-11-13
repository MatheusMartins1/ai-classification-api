"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Service for extracting thermal and visual data from FLIR thermal images.
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva.
"""

import json
import os
import sys
from typing import Any, Dict, Optional, Union

import cv2
import flyr  # type: ignore
import numpy as np  # type: ignore
import pandas as pd  # type: ignore
from pydantic_core.core_schema import none_schema

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(base_dir)
sys.path.append(base_dir)

from config import settings as settings_module

# settings_module.settings = settings_module.Settings(base_dir=base_dir)
settings = settings_module.settings

from services.exiftool_extractor import ExifToolExtractor
from services.measurement_extractor import MeasurementExtractor
from services.supabase_handler import SupabaseStorageHandler
from services.thermal_data_builder import ThermalDataBuilder
from utils import object_handler
from utils import temperature_calculations as thermal_calculations
from utils.LoggerConfig import LoggerConfig
from utils.object_handler import extract_all_attributes

logger = LoggerConfig.add_file_logger(
    name="image_data_extractor",
    filename=None,
    dir_name=None,
    prefix="data_extractor",
    level_name="INFO",
)


def extract_data_from_image(
    image_name: str = "FLIR1970.jpg", form_data: Optional[dict] = None
) -> dict:
    """
    Extract thermal data from FLIR image using ThermalDataBuilder.

    Args:
        image_name: Name of the FLIR image file
        form_data: Form data containing tag and other metadata

    Returns:
        Dictionary with extraction results and metadata
    """
    form_data = form_data or {}
    # Parse image name
    image_name_parts = image_name.split(".")
    image_filename = image_name_parts[0]
    image_folder = os.path.join("temp", image_filename)

    # Create folder structure
    os.makedirs(image_folder, exist_ok=True)

    # Build IR filename
    ir_filename = f"{image_filename}_IR.{image_name_parts[1]}"
    image_path = os.path.join(image_folder, ir_filename)

    # Unpack thermogram
    logger.info(f"Unpacking thermogram from: {image_path}")
    thermogram = flyr.unpack(image_path)

    # Initialize ThermalDataBuilder
    thermal_builder = ThermalDataBuilder(temp_folder="temp")

    # Extract EXIF metadata using ExifTool
    logger.info("Extracting EXIF metadata with ExifTool...")
    exiftool_extractor = ExifToolExtractor()
    exiftool_metadata = exiftool_extractor.extract_metadata(image_path)

    if exiftool_metadata:
        logger.info("EXIF metadata extracted successfully")
    else:
        logger.warning("Failed to extract EXIF metadata, continuing without it")

    # Build complete thermal image data with all conversions
    logger.info("Building complete ThermalImageData...")
    thermal_data = thermal_builder.build_thermal_image_data(
        thermogram=thermogram,
        image_name=image_name,
        save_files=True,
        form_data=form_data,
        exiftool_metadata=exiftool_metadata,  # type: ignore
    )

    # Save optical image
    logger.info("Saving optical image...")
    optical_filename = f"{image_filename}_REAL.jpg"
    thermogram.optical_pil.save(os.path.join(image_folder, optical_filename))

    # Convert to dictionary
    thermal_data_dict = thermal_data.model_dump(exclude_none=True)

    # Calculate additional statistics (severity grade)
    calculations = _calculate_additional_statistics(thermal_data)
    thermal_data_dict["calculations"] = calculations

    # Save metadata JSON
    json_filename = os.path.join(image_folder, f"{image_filename}_metadata.json")
    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump(thermal_data_dict, json_file, indent=2, ensure_ascii=False)

    logger.info(f"Metadata extraction completed for: {image_name}")

    # Build response
    response_dict = {
        "success": True,
        "message": "Metadata extracted successfully",
        "metadata": thermal_data_dict,
    }

    return response_dict


def _calculate_additional_statistics(thermal_data) -> dict:
    """
    Calculate additional statistics like severity grade.

    Args:
        thermal_data: ThermalImageData object

    Returns:
        Dictionary with additional calculations
    """
    calculations = {}

    try:
        if thermal_data.temperature_data:
            temp_data = thermal_data.temperature_data

            # Get basic statistics
            min_temp = temp_data.min_temperature
            max_temp = temp_data.max_temperature
            delta_t = temp_data.delta_t

            # Calculate std deviation from celsius array
            if temp_data.celsius:
                celsius_np = np.array(temp_data.celsius)
                std_dev = (
                    thermal_calculations.get_standard_deviation_from_temperature_array(
                        celsius_np
                    )
                )
                variance = thermal_calculations.get_variance_from_temperature_array(
                    celsius_np
                )
            else:
                std_dev = 0.0
                variance = 0.0

            # Calculate severity grade
            severity_result = thermal_calculations.generate_severity_grade(
                delta_t=delta_t if delta_t else 0.0,
                std_dev=std_dev,
            )

            calculations = {
                "min_temperature": min_temp,
                "max_temperature": max_temp,
                "avg_temperature": temp_data.avg_temperature,
                "median_temperature": temp_data.median_temperature,
                "standard_deviation": std_dev,
                "variance": variance,
                "delta_t": delta_t,
                "severity_result": severity_result,
            }

    except Exception as e:
        logger.error(f"Error calculating additional statistics: {e}")

    return calculations


def extract_measurements(thermogram: Any, celsius_array: Any = None) -> list:
    """
    Extract measurements from a thermogram with temperature statistics.

    Args:
        thermogram: Thermogram object from flyr
        celsius_array: Temperature matrix in Celsius (numpy array)

    Returns:
        List of Measurement dictionaries with temperature statistics
    """
    measurement_extractor = MeasurementExtractor()
    measurements = measurement_extractor.extract_measurements(thermogram, celsius_array)

    # Convert Measurement objects to dictionaries for JSON serialization
    return [measurement.model_dump(exclude_none=True) for measurement in measurements]


def format_json_data(data: dict) -> dict:
    return {}


async def send_data_to_storage(response_data: dict) -> bool:
    """
    Save files into supabase storage using SupabaseStorageHandler.

    Args:
        response_data: Dictionary containing IR images and user info

    Returns:
        True if all uploads succeed, False otherwise
    """
    storage_handler = SupabaseStorageHandler()
    return await storage_handler.send_data_to_storage(response_data)


if __name__ == "__main__":
    extract_data_from_image()
