"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Service for extracting thermal and visual data from FLIR thermal images.
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva.
"""

import asyncio
import json
import os
import shutil
import subprocess
import sys
from typing import Any, Dict, Optional, Union

import cv2
import flyr
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
from utils.supabase_client import SupabaseService

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

    # Save Optical image to temp folder
    thermogram.optical_pil.save(
        os.path.join(image_folder, f"{image_filename}_REAL.jpg")
    )

    image_metadata = {
        "storage_info": thermogram_data.get("storage_info", {}),
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
                    logger.info(
                        f"Warning: Could not extract {attr} from {description}: {e}"
                    )
                    continue
    except Exception as e:
        logger.info(f"Warning: Could not iterate attributes of {description}: {e}")
        return str(obj)

    return result


async def send_data_to_database(response_data: dict):
    """
    Save files into supabase storage
    """
    supabase_service = SupabaseService()
    supabase_client = supabase_service.client
    bucket_name = "imagem"
    files = ["image_saved_ir_filename", "image_saved_real_filename"]

    task_success = []

    for index, image in enumerate(response_data["ir_images"]):
        storage_info = image.get("metadata", {}).get("storage_info", {})
        image_path = os.path.join(storage_info.get("image_folder", ""))

        for file in files:
            file_path = "/".join(
                [
                    "companies",
                    response_data.get("user_info", {}).get("company_id", ""),
                    storage_info.get("image_filename", ""),
                    storage_info.get(file, ""),
                ]
            )

            file_data = open(
                os.path.join(image_path, storage_info.get(file, "")),
                "rb",
            ).read()

            content_type = image["content_type"]
            try:
                #TODO: Check what happens if multiple files are uploaded at the same time
                await asyncio.to_thread(
                    supabase_service.upload_file,
                    bucket_name=bucket_name,
                    file_path=file_path,
                    file_data=file_data,
                    content_type=content_type,
                    if_exists="overwrite",
                )
                task_success.append(True)
            except Exception as e:
                logger.error(f"Error uploading file: {e}")
                task_success.append(False)
                raise e
        
        try:
            file_name = f"{storage_info.get("image_filename", "")}_temperature.csv"
            #Send temperature.csv to storage
            temperature_csv_path = "/".join([
                "companies",
                response_data.get("user_info", {}).get("company_id", ""),
                storage_info.get("image_filename", ""),
                file_name,
            ])
            file_data = open(os.path.join(image_path, file_name), "rb").read()
            await asyncio.to_thread(
                supabase_service.upload_file,
                bucket_name=bucket_name,
                file_path=temperature_csv_path,
                file_data=file_data,
                if_exists="overwrite",
            )
            task_success.append(True)
        except Exception as e:
            logger.error(f"Error uploading temperature.csv: {e}")
            task_success.append(False)
            raise e

        try:
            file_name = f"{storage_info.get("image_filename", "")}_temperature.json"
            #Send temperature.json to storage
            temperature_json_path = "/".join([
                "companies",
                response_data.get("user_info", {}).get("company_id", ""),
                storage_info.get("image_filename", ""),
                file_name,
            ])
            file_data = open(os.path.join(image_path, file_name), "rb").read()
            await asyncio.to_thread(
                supabase_service.upload_file,
                bucket_name=bucket_name,
                file_path=temperature_json_path,
                file_data=file_data,
                if_exists="overwrite",
            )
            task_success.append(True)
        except Exception as e:
            logger.error(f"Error uploading temperature.json: {e}")
            task_success.append(False)
            raise e

    if all(task_success):
        #remove temp folder
        shutil.rmtree(image_path)
        return True
    else:
        #TODO: Reprocess the image
        return False

if __name__ == "__main__":
    extract_data_from_image()
