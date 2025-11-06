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


# TODO: sync with ZoomSettings class
class ZoomInfo:
    """
    ZoomInfo provides basic methods to handle zoom information.
    """

    def __init__(self, _camera):
        """
        Initialize the ZoomInfo class with a camera instance.
        """
        self._camera = _camera
        self.logger = _camera.logger
        self._service_lock = _camera.service_lock

        self._thermal_image = _camera.image_obj_thermal
        self._visual_image = _camera.image_obj_visual
        self.is_supported = True

        self.Factor = None
        self.PanX = None
        self.PanY = None

        self._check_if_supported(self._thermal_image)

    def _check_if_supported(self, thermal_image: Optional[Any] = None):
        """
        Check if the zoom information is supported by the camera.
        """
        if thermal_image is None and self._thermal_image is None:
            self.is_supported = False
            return

        try:
            if thermal_image.Zoom is None:
                self.is_supported = False
                return
        except Exception as e:
            self.is_supported = False
            return

        self.is_supported = True

    def update_info(self, thermal_image: Optional[Any] = None) -> None:
        """
        Update the zoom information from the thermal image.
        """
        with self._service_lock:
            if thermal_image is None and self._thermal_image is None:
                return

            thermal_image = (
                thermal_image
                if isinstance(thermal_image, Image.ThermalImage)
                else self._thermal_image
            )

            zoom_info = self.extract_zoom_information(thermal_image)

            if zoom_info is not None:
                self.Factor = zoom_info.get("Factor")
                self.PanX = zoom_info.get("PanX")
                self.PanY = zoom_info.get("PanY")

    def extract_zoom_information(self, thermal_image: Any) -> Optional[Dict[str, Any]]:
        """
        Safely extract zoom information from thermal image.

        Args:
            thermal_image: Thermal image object

        Returns:
            Zoom information dictionary or None if not available
        """
        self._check_if_supported(thermal_image)
        if thermal_image.Zoom is None:
            return None

        try:
            zoom_info = thermal_image.Zoom
            return {
                "Factor": object_handler.safe_extract_attribute(
                    zoom_info, "Factor", convert_type="float", float_precision=2
                ),
                "PanX": object_handler.safe_extract_attribute(
                    zoom_info, "PanX", convert_type="float", float_precision=2
                ),
                "PanY": object_handler.safe_extract_attribute(
                    zoom_info, "PanY", convert_type="float", float_precision=2
                ),
            }
        except Exception as e:
            self.logger.warning(f"Error extracting zoom information: {e}")
            return None

    def set_zoom_info(self, zoom_info: Dict[str, Any]) -> None:
        # TODO: Implement this method
        pass

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert zoom information to dictionary format.

        Returns:
            Dictionary containing zoom information
        """
        return {
            "Factor": self.Factor,
            "PanX": self.PanX,
            "PanY": self.PanY,
        }
