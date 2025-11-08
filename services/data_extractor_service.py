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

from pydantic_core.core_schema import none_schema

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("Base directory: ", base_dir)
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
    image_path = os.path.join("temp", image_name)

    thermogram = flyr.unpack(image_path)
    # Initialize data structure
    thermogram_data = {
        "image_filename": image_name,
        "image_path": image_path,
    }

    # Extract all thermogram attributes automatically
    print("Extracting all thermogram attributes...")
    try:
        all_data = extract_all_attributes(thermogram, "thermogram")
        thermogram_data.update(all_data)

    except Exception as e:
        print(f"Error extracting thermogram data: {e}")
        celsius_array = None

    celsius_array = thermogram_data.get("celsius", None)

    # Save Optical image to temp folder
    thermogram.optical_pil.save(os.path.join("temp", f"{image_name}_optical.jpg"))

    image_metadata = {
        "image_filename": thermogram_data.get("image_filename", None),
        "image_path": thermogram_data.get("image_path", None),
        "metadata": thermogram_data.get("metadata", None),
        "camera_metadata": thermogram_data.get("camera_metadata", None),
        "palette": thermogram_data.get("palette", None),
        "pip_info": thermogram_data.get("pip_info", None),
    }

    # save json file
    json_filename = os.path.join("temp", f"{image_name}_metadata.json")
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
                            result[attr] = list(value)
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
                    print(f"Warning: Could not extract {attr} from {description}: {e}")
                    continue
    except Exception as e:
        print(f"Warning: Could not iterate attributes of {description}: {e}")
        return str(obj)

    return result


if __name__ == "__main__":
    extract_data_from_image()
