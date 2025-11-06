"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

import os
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


class ZoomSettings:
    """
    A class to manage the camera zoom settings.

    Reference:
    https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/class_flir_1_1_atlas_1_1_image_1_1_zoom_settings.html
    """

    def __init__(self, _camera):
        """
        Initialize the ZoomSettings class.

        Args:
            _camera: The camera instance to control.
        """
        self._camera = _camera
        self.logger = _camera.logger

        self.image_obj_thermal = _camera.image_obj_thermal

        self.factor = None
        self.pan_x = None
        self.pan_y = None

        self.update_settings()

    def update_settings(self) -> None:
        """
        Update all zoom settings by retrieving current values from the camera.
        """
        self.get_zoom()

    def get_zoom(self) -> Optional[float]:
        """
        Get the current zoom factor.

        Returns:
            Optional[float]: The zoom magnification factor, or None if error occurs.
        """
        try:
            factor = self.image_obj_thermal.Zoom.Factor
        except Exception as e:
            self.logger.error(e)

        try:
            ZoomAndPan = self.image_obj_thermal.GetZoomAndPan
            self.zoom = ZoomAndPan
        except Exception as e:
            self.logger.error(e)
            return None

        return factor

    def set_zoom_factor(self, factor: float) -> None:
        """
        Set the zoom magnification factor.

        Args:
            factor (float): The zoom factor value (1.0 or greater).
        """
        try:
            self.image_obj_thermal.Zoom.Factor = factor
            self.factor = factor
        except Exception as e:
            self.logger.error(e)

    def set_pan_x(self, value: float) -> None:
        """
        Set the horizontal zoom starting point.

        Args:
            value (float): The horizontal pan position (0.0 to 1.0).
        """
        try:
            self._camera._thermal_image.Zoom.PanX = value
            self.pan_x = value
        except Exception as e:
            self.logger.error(e)

    def set_pan_y(self, value: float) -> None:
        """
        Set the vertical zoom starting point.

        Args:
            value (float): The vertical pan position (0.0 to 1.0).
        """
        try:
            self._camera._thermal_image.Zoom.PanY = value
            self.pan_y = value
        except Exception as e:
            self.logger.error(e)

    def set_zoom_pan(self, pan_x: float, pan_y: float) -> None:
        """
        Set both horizontal and vertical zoom starting points.

        Args:
            pan_x (float): The horizontal pan position (0.0 to 1.0).
            pan_y (float): The vertical pan position (0.0 to 1.0).
        """
        self.set_pan_x(pan_x)
        self.set_pan_y(pan_y)

    def to_string(self) -> Dict[str, Any]:
        """
        Return all zoom settings properties in a dictionary format.

        Returns:
            Dict[str, Any]: Dictionary containing current zoom settings.
        """
        return {"factor": self.factor, "pan_x": self.pan_x, "pan_y": self.pan_y}
