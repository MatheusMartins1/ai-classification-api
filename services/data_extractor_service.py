"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Service for extracting thermal and visual data from FLIR thermal images.
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva.
"""

import os
import subprocess
import sys
import cv2
from typing import Any, Dict, Optional, Union
import flyr
import json
import pandas as pd

from pydantic_core.core_schema import none_schema

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(base_dir)
sys.path.append(base_dir)

from config import settings as settings_module

# settings_module.settings = settings_module.Settings(base_dir=base_dir)
settings = settings_module.settings

from utils import object_handler
from utils.LoggerConfig import LoggerConfig

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
        "image_filename": image_filename,
        "image_folder": image_folder,
        "image_extension": image_name_splited[1],
        "image_saved_ir_filename": f"{image_name_splited[0]}_IR.{image_name_splited[1]}",
        "image_saved_real_filename": f"{image_name_splited[0]}_REAL.{image_name_splited[1]}",
    }

    thermogram = flyr.unpack(os.path.join(image_folder, thermogram_data["image_saved_ir_filename"]))

    # Extract all thermogram attributes automatically
    logger.info("Extracting all thermogram attributes...")
    try:
        all_data = extract_all_attributes(thermogram, "thermogram")
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
        os.path.join(image_folder, f"{image_filename}_temperature.json"), orient="records"
    )

    # Save Optical image to temp folder
    thermogram.optical_pil.save(os.path.join(image_folder, f"{image_filename}_REAL.jpg"))

    image_metadata = {
        "image_filename": thermogram_data.get("image_filename", None),
        "image_folder": thermogram_data.get("image_folder", None),
        "metadata": thermogram_data.get("metadata", None),
        "camera_metadata": thermogram_data.get("camera_metadata", None),
        "palette": thermogram_data.get("palette", None),
        "pip_info": thermogram_data.get("pip_info", None),
        "temperature_json": temperature_dict,
    }

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


def extract_all_attributes(obj, description="", max_depth=3, current_depth=0):
    """Recursively extract all attributes from an object"""
    if current_depth >= max_depth:
        return str(obj)

    result = {}

    try:
        for attr in dir(obj):
            if not attr.startswith("_") and not callable(getattr(obj, attr)):
                try:
                    value = getattr(obj, attr)
                    if value is not None:
                        # Handle different types of values
                        if hasattr(value, "tolist"):
                            result[attr] = value.tolist()
                        elif isinstance(value, (str, int, float, bool)):
                            result[attr] = value
                        elif isinstance(value, (list, tuple)):
                            result[attr] = list[Any](value)
                        elif isinstance(value, dict):
                            # Handle dictionary with potential non-serializable values
                            clean_dict = {}
                            for k, v in value.items():
                                try:
                                    json.dumps(v)
                                    clean_dict[k] = v
                                except (TypeError, ValueError):
                                    # Convert non-serializable values to string or float
                                    if hasattr(v, "__float__"):
                                        try:
                                            clean_dict[k] = float(v)
                                        except:
                                            clean_dict[k] = str(v)
                                    # Binary data
                                    elif isinstance(v, bytes):
                                        try:
                                            clean_dict[k] = v.decode("utf-8")
                                        except:
                                            clean_dict[k] = str(v)
                                    else:
                                        clean_dict[k] = str(v)
                            result[attr] = clean_dict
                        elif hasattr(value, "__dict__"):
                            # Recursively extract nested objects
                            result[attr] = extract_all_attributes(
                                value,
                                f"{description}.{attr}",
                                max_depth,
                                current_depth + 1,
                            )
                        # Binary data
                        elif isinstance(value, bytes):
                            try:
                                result[attr] = value.decode("utf-8")
                            except:
                                result[attr] = str(value)
                        else:
                            try:
                                json.dumps(value)  # Test if JSON serializable
                                result[attr] = value
                            except (TypeError, ValueError):
                                # Handle non-serializable types (like IFDRational)
                                if hasattr(value, "__float__"):
                                    try:
                                        result[attr] = float(value)
                                    except:
                                        result[attr] = str(value)
                                else:
                                    result[attr] = str(value)
                except Exception as e:
                    logger.info(f"Warning: Could not extract {attr} from {description}: {e}")
                    continue
    except Exception as e:
        logger.info(f"Warning: Could not iterate attributes of {description}: {e}")
        return str(obj)

    return result


async def send_data_to_database(response_data: dict):
    try:
        # Send data to database
        logger.info(f"Sending data to database: {response_data}")
    except Exception as e:
        logger.error(f"Error sending data to database: {e}")
        raise e


if __name__ == "__main__":
    extract_data_from_image()
