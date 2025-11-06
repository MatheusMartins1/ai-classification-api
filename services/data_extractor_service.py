import os
import sys
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("Base directory: ", base_dir)
os.chdir(base_dir)
sys.path.append(base_dir)


from typing import Any, Dict, Optional, Union
import clr

from config.settings import settings
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

from camera.image.image_service import ImageDataService
from camera.services.data_extractor import DataExtractorService

# Add the path to the directory containing the compiled DLL
DLL_PATH = os.path.join(settings.BASE_DIR, "ThermalCameraLibrary")

clr.AddReference(os.path.join(DLL_PATH, "ThermalCamera.dll"))
clr.AddReference(os.path.join(DLL_PATH, "Flir.Atlas.Live.dll"))
clr.AddReference(os.path.join(DLL_PATH, "Flir.Atlas.Image.dll"))
clr.AddReference("System")

import Flir.Atlas.Image as Image  # type: ignore

def extract_data_from_image(
    image_name: str = "FLIR1970.jpg", data_to_extract: str = "complete"
) -> dict:
    image_path = os.path.join("temp", image_name)
    thermal_image = Image.ThermalImageFile(image_path)
    # save_visual_image(thermal_image, image_name)

    thermal_data = DataExtractorService.extract_thermal_data(
        thermal_image, data_to_extract, camera=None
    )

    view_response = DataExtractorService.format_response_for_view(
        thermal_data, data_to_extract
    )

    return view_response


def save_visual_image(thermal_image, image_name: str = "FLIR1970.jpg") -> None:
    visual_image = thermal_image.Image
    visual_image.Save(f"temp/{image_name}_visual.jpg")


if __name__ == "__main__":
    view_response = extract_data_from_image()
    print(view_response)

# C:\projects\tenesso\ai\ai-regression-api
