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
from typing import Any, Dict, Optional, Union

import clr  # type: ignore

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("Base directory: ", base_dir)
os.chdir(base_dir)
sys.path.append(base_dir)


from config import settings as settings_module

# settings_module.settings = settings_module.Settings(base_dir=base_dir)
settings = settings_module.settings

from utils import object_handler
from utils.infrastructure import get_local_ip
from utils.LoggerConfig import LoggerConfig

logger = LoggerConfig.add_file_logger(
    name="image_data_extractor",
    filename=None,
    dir_name=None,
    prefix="data_extractor",
    level_name="ERROR",
)

from camera.image.image_extraction import ImageExtractor
from camera.image.image_service import ImageDataService
from camera.services.data_extractor import DataExtractorService

# Add the path to the directory containing the compiled DLL
DLL_PATH = os.path.join(settings.BASE_DIR, "ThermalCameraLibrary")
sys.path.append(DLL_PATH)

clr.AddReference(os.path.join(DLL_PATH, "ThermalCamera.dll"))
clr.AddReference(os.path.join(DLL_PATH, "Flir.Atlas.Live.dll"))
clr.AddReference(os.path.join(DLL_PATH, "Flir.Atlas.Image.dll"))
clr.AddReference("System")

import Flir.Atlas.Image as Image  # type: ignore

image_extractor = ImageExtractor(None)


def extract_data_from_image(
    image_name: str = "FLIR1970.jpg", data_to_extract: str = "complete"
) -> dict:
    image_path = os.path.join("temp", image_name)
    thermal_image = Image.ThermalImageFile(image_path)
    # save_visual_image(thermal_image, image_name)
    image_bitmap_visual = ImageExtractor.get_image(
        image_extractor, thermal_image, img_type="bitmap"
    )
    image_visual_np = ImageExtractor.convert_image_to_numpy(
        image_extractor, image_bitmap_visual
    )

    thermal_data = DataExtractorService.extract_thermal_data(
        thermal_image, data_to_extract, camera=None
    )

    view_response = DataExtractorService.format_response_for_view(
        thermal_data, data_to_extract
    )

    extract_flir_images(image_path, "temp")

    return view_response


def save_visual_image(thermal_image, image_name: str = "FLIR1970.jpg") -> None:
    visual_image = thermal_image.Image
    visual_image.Save(f"temp/{image_name}_visual.jpg")


def extract_flir_images(
    image_path: str, output_folder: str
) -> Dict[str, Optional[str]]:
    """
    Extract visual and thermal images from a FLIR JPG file using exiftool.

    Args:
        image_path: Path to the FLIR JPG file.
        output_folder: Folder where extracted images will be saved.

    Returns:
        Dictionary containing paths to extracted images:
        {
            "visual_image": str or None,
            "thermal_image": str or None,
            "embedded_image": str or None
        }

    Raises:
        FileNotFoundError: If exiftool is not found in system PATH.
        ValueError: If image_path does not exist.
    """
    if not os.path.exists(image_path):
        error_msg = f"Arquivo de imagem não encontrado: {image_path}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        logger.info(f"Pasta de saída criada: {output_folder}")

    base_name = os.path.splitext(os.path.basename(image_path))[0]
    result: Dict[str, Optional[str]] = {
        "visual_image": None,
        "thermal_image": None,
        "embedded_image": None,
    }

    # Check if exiftool is available
    try:
        subprocess.run(["exiftool", "-ver"], capture_output=True, check=True, timeout=5)
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ) as e:
        error_msg = "exiftool não encontrado. Instale em: https://exiftool.org/"
        logger.error(f"{error_msg} - Erro: {str(e)}")
        raise FileNotFoundError(error_msg) from e

    # Extract visual preview image
    try:
        visual_path = os.path.join(output_folder, f"{base_name}_visual.jpg")
        with open(visual_path, "wb") as f:
            result_proc = subprocess.run(
                ["exiftool", "-b", "-PreviewImage", image_path],
                capture_output=True,
                check=True,
                timeout=10,
            )
            f.write(result_proc.stdout)

        if os.path.exists(visual_path) and os.path.getsize(visual_path) > 0:
            result["visual_image"] = visual_path
            logger.info(f"Imagem visual extraída: {visual_path}")
        else:
            logger.warning("Nenhuma imagem visual (PreviewImage) encontrada")
            if os.path.exists(visual_path):
                os.remove(visual_path)
    except subprocess.CalledProcessError as e:
        logger.error(
            f"Erro ao extrair imagem visual: {e.stderr.decode() if e.stderr else str(e)}"
        )
    except Exception as e:
        logger.error(f"Erro inesperado ao extrair imagem visual: {str(e)}")

    # Extract embedded thermal image
    try:
        embedded_path = os.path.join(output_folder, f"{base_name}_thermal_embedded.jpg")
        with open(embedded_path, "wb") as f:
            result_proc = subprocess.run(
                ["exiftool", "-b", "-EmbeddedImage", image_path],
                capture_output=True,
                check=True,
                timeout=10,
            )
            f.write(result_proc.stdout)

        if os.path.exists(embedded_path) and os.path.getsize(embedded_path) > 0:
            result["embedded_image"] = embedded_path
            logger.info(f"Imagem térmica embutida extraída: {embedded_path}")
        else:
            logger.warning("Nenhuma imagem térmica (EmbeddedImage) encontrada")
            if os.path.exists(embedded_path):
                os.remove(embedded_path)
    except subprocess.CalledProcessError as e:
        logger.error(
            f"Erro ao extrair imagem térmica embutida: {e.stderr.decode() if e.stderr else str(e)}"
        )
    except Exception as e:
        logger.error(f"Erro inesperado ao extrair imagem térmica embutida: {str(e)}")

    # Extract raw thermal image data
    try:
        raw_thermal_path = os.path.join(output_folder, f"{base_name}_thermal_raw.dat")
        with open(raw_thermal_path, "wb") as f:
            result_proc = subprocess.run(
                ["exiftool", "-b", "-RawThermalImage", image_path],
                capture_output=True,
                check=True,
                timeout=10,
            )
            f.write(result_proc.stdout)

        if os.path.exists(raw_thermal_path) and os.path.getsize(raw_thermal_path) > 0:
            result["thermal_image"] = raw_thermal_path
            logger.info(f"Dados térmicos brutos extraídos: {raw_thermal_path}")
        else:
            logger.warning("Nenhuma imagem térmica bruta (RawThermalImage) encontrada")
            if os.path.exists(raw_thermal_path):
                os.remove(raw_thermal_path)
    except subprocess.CalledProcessError as e:
        logger.error(
            f"Erro ao extrair dados térmicos brutos: {e.stderr.decode() if e.stderr else str(e)}"
        )
    except Exception as e:
        logger.error(f"Erro inesperado ao extrair dados térmicos brutos: {str(e)}")

    return result


if __name__ == "__main__":
    view_response = extract_data_from_image()
    print(view_response)

# C:\projects\tenesso\ai\ai-regression-api
