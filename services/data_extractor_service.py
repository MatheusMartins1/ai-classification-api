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
import pandas as pd  # type: ignore
from pydantic_core.core_schema import none_schema

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(base_dir)
sys.path.append(base_dir)

from config import settings as settings_module

# settings_module.settings = settings_module.Settings(base_dir=base_dir)
settings = settings_module.settings

from services.supabase_handler import SupabaseStorageHandler
from utils import object_handler
from utils.LoggerConfig import LoggerConfig
from utils.object_handler import extract_all_attributes

logger = LoggerConfig.add_file_logger(
    name="image_data_extractor",
    filename=None,
    dir_name=None,
    prefix="data_extractor",
    level_name="INFO",
)


def extract_data_from_image(image_name: str = "FLIR1970.jpg") -> dict:
    image_name_splited = image_name.split(".")
    image_filename = image_name_splited[0]
    image_folder = os.path.join("temp", image_filename)
    os.makedirs(os.path.join("temp", image_filename), exist_ok=True)

    # Initialize data structure
    thermogram_data = {
        "storage_info": {
            "image_filename": image_filename,
            "image_folder": image_folder,
            "image_extension": image_name_splited[1],
            "image_saved_ir_filename": f"{image_name_splited[0]}_IR.{image_name_splited[1]}",
            "image_saved_real_filename": f"{image_name_splited[0]}_REAL.{image_name_splited[1]}",
        }
    }

    thermogram = flyr.unpack(
        os.path.join(
            image_folder,
            thermogram_data.get("storage_info", {}).get("image_saved_ir_filename", ""),
        )
    )

    # Extract all thermogram attributes automatically
    logger.info("Extracting all thermogram attributes...")
    try:
        all_data = extract_all_attributes(thermogram, "thermogram")
        if isinstance(all_data, dict):
            thermogram_data.update(all_data)

    except Exception as e:
        logger.info(f"Error extracting thermogram data: {e}")
        celsius_array = None

    celsius_array = thermogram_data.get("celsius", None)
    temperature_df = pd.DataFrame(celsius_array)
    temperature_dict = temperature_df.to_dict(orient="records")
    temperature_df.to_csv(
        os.path.join(image_folder, f"{image_filename}_temperature.csv"), index=False
    )
    temperature_df.to_json(
        os.path.join(image_folder, f"{image_filename}_temperature.json"),
        orient="records",
    )
    measurements = extract_measurements(thermogram)

    # save

    # Save Optical image to temp folder
    thermogram.optical_pil.save(
        os.path.join(image_folder, f"{image_filename}_REAL.jpg")
    )

    image_metadata = {
        "storage_info": thermogram_data.get("storage_info", {}),
        "metadata": thermogram_data.get("metadata", None),
        "camera_metadata": thermogram_data.get("camera_metadata", None),
        # "palette": thermogram_data.get("palette", None),
        "pip_info": thermogram_data.get("pip_info", None),
        # "temperature_json": temperature_dict,
    }

    # NS câmera - X
    # Emissividade - V
    # Temperatura média refletida - V
    # Temperatura Atmosférica - V
    # Relative humidity: - V
    # Ext optics temperature - all_data['metadata']['ir_window_temperature']
    # Ext optics Transmission - all_data['metadata']['ir_window_transmission']
    # Faixa de temperatura - all_data['metadata']['temperature_range']

    # save json file
    json_filename = os.path.join(image_folder, f"{image_filename}_metadata.json")
    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump(image_metadata, json_file, indent=2, ensure_ascii=False)

    response_dict = {
        "success": True,
        "message": "Metadata extracted successfully",
        "metadata": image_metadata,
    }

    return response_dict


def extract_measurements(thermogram: Any) -> Optional[dict]:
    """
    Extract measurements from a thermogram.
    """
    return None  # FIXME: Implement this


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
