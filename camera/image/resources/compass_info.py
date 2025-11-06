"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

import os
from threading import Lock
from typing import Any, Dict, Optional

import clr

from config.settings import settings

# Add the path to the directory containing the compiled DLL
dll_path = os.path.join(settings.BASE_DIR, "ThermalCameraLibrary")

clr.AddReference(os.path.join(dll_path, "ThermalCamera.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Live.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Image.dll"))
clr.AddReference("System")

import Flir.Atlas.Image as Image  # type: ignore

# Import the necessary classes from the assembly
import Flir.Atlas.Live as live  # type: ignore

from utils import object_handler


class CompassInfo:
    """
    CompassInfo provides basic methods to handle compass information.
    """

    def __init__(self, _camera):
        """
        Initialize the CompassInfo class with a camera instance.
        """
        self._camera = _camera
        self.logger = _camera.logger
        self._service_lock = _camera.service_lock

        self._thermal_image = _camera.image_obj_thermal
        self._visual_image = _camera.image_obj_visual
        self.is_supported = True

        self.Degrees = None
        self.Roll = None
        self.Pitch = None

        self._check_if_supported(self._thermal_image)

    def _check_if_supported(self, thermal_image: Optional[Any] = None):
        """
        Check if the compass information is supported by the camera.
        """
        if thermal_image is None and self._thermal_image is None:
            self.is_supported = False
            return

        try:
            if thermal_image.CompassInformation is None:
                self.is_supported = False
                return
        except Exception as e:
            self.is_supported = False
            return

        self.is_supported = True

    def update_info(self, thermal_image: Optional[Any] = None) -> None:
        """
        Update the compass information from the thermal image.
        """
        with self._service_lock:
            if thermal_image is None and self._thermal_image is None:
                return

            thermal_image = (
                thermal_image
                if isinstance(thermal_image, Image.ThermalImage)
                else self._thermal_image
            )

            compass_info = self.extract_compass_information(thermal_image)

            if compass_info is not None:
                self.Degrees = compass_info.get("Degrees")
                self.Roll = compass_info.get("Roll")
                self.Pitch = compass_info.get("Pitch")

    def set_compass_info(self, compass_info: Dict[str, Any]) -> None:
        # TODO: Implement this method
        pass

    def extract_compass_information(
        self, thermal_image: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Safely extract compass information from thermal image.

        Args:
            thermal_image: Thermal image object

        Returns:
            Compass information dictionary or None if not available
        """
        self._check_if_supported(thermal_image)
        try:
            if thermal_image.CompassInformation is None:
                return None
        except Exception as e:
            self.logger.warning(f"Error accessing CompassInformation: {e}")
            return None

        try:
            compass_info = thermal_image.CompassInformation
            return {
                "Degrees": object_handler.safe_extract_attribute(
                    compass_info, "Degrees", convert_type="int"
                ),
                "Roll": object_handler.safe_extract_attribute(
                    compass_info, "Roll", convert_type="int"
                ),
                "Pitch": object_handler.safe_extract_attribute(
                    compass_info, "Pitch", convert_type="int"
                ),
            }
        except Exception as e:
            self.logger.warning(f"Error extracting compass information: {e}")
            return None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert compass information to dictionary format.

        Returns:
            Dictionary containing compass information
        """
        return {
            "Degrees": self.Degrees,
            "Roll": self.Roll,
            "Pitch": self.Pitch,
        }
