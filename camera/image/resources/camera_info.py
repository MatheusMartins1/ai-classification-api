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


class CameraInfo:
    """
    CameraInfo provides basic methods to handle camera information.
    """

    def __init__(self, _camera):
        """
        Initialize the CameraInfo class with a camera instance.
        """
        self._camera = _camera
        self.logger = _camera.logger
        self._service_lock = _camera.service_lock

        self._thermal_image = _camera.image_obj_thermal
        self._visual_image = _camera.image_obj_visual
        self.is_supported = True

        self.Model = None
        self.SerialNumber = None
        self.Lens = None
        self.Filter = None
        self.Fov = None
        self.Range = {"Maximum": None, "Minimum": None}

        self.Fps = None
        self.AveragePayload = None
        self.FrameCount = None
        self.FrameRateIndex = None
        self.LostImages = None
        self.TimelapseReconnect = None
        self.TimeoutCheckForHeartbeat = None

        self._check_if_supported(self._thermal_image)

    def _check_if_supported(self, thermal_image: Optional[Any] = None):
        """
        Check if the camera information is supported by the camera.
        """
        if thermal_image is None and self._thermal_image is None:
            self.is_supported = False
            return

        try:
            if thermal_image.CameraInformation is None:
                self.is_supported = False
                return
        except Exception as e:
            self.is_supported = False
            return

        self.is_supported = True

    def update_info(self, thermal_image: Optional[Any] = None) -> None:
        """
        Update the camera information from the thermal image.
        """
        with self._service_lock:
            if thermal_image is None and self._thermal_image is None:
                return

            thermal_image = (
                thermal_image
                if isinstance(thermal_image, Image.ThermalImage)
                else self._thermal_image
            )

            camera_info = self.extract_camera_information(thermal_image)

            if camera_info is not None:
                self.Range = camera_info.get("Range")
                self.Model = camera_info.get("Model")
                self.SerialNumber = camera_info.get("SerialNumber")
                self.Lens = camera_info.get("Lens")
                self.Filter = camera_info.get("Filter")
                self.Fov = camera_info.get("Fov")
                self.Fps = camera_info.get("Fps")
                self.AveragePayload = camera_info.get("AveragePayload")
                self.FrameCount = camera_info.get("FrameCount")
                self.FrameRateIndex = camera_info.get("FrameRateIndex")
                self.LostImages = camera_info.get("LostImages")
                self.TimelapseReconnect = camera_info.get("TimelapseReconnect")
                self.TimeoutCheckForHeartbeat = camera_info.get(
                    "TimeoutCheckForHeartbeat"
                )

    def extract_camera_information(
        self, thermal_image: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Safely extract camera information from thermal image.

        Args:
            thermal_image: Thermal image object

        Returns:
            Camera information dictionary or None if not available
        """
        self._check_if_supported(thermal_image)
        if thermal_image.CameraInformation is None:
            return None

        try:
            if self._camera and self._camera.fps is None or self._camera.fps == 0:
                self._camera.connection_manager.fill_camera_info()
        except Exception as e:
            self.logger.warning(f"Error filling camera information: {e}")

        try:
            camera_info_obj = thermal_image.CameraInformation
            camera_info = {
                "Model": object_handler.safe_extract_attribute(
                    camera_info_obj, "Model"
                ),
                "SerialNumber": object_handler.safe_extract_attribute(
                    camera_info_obj, "SerialNumber", convert_type="str"
                ),
                "Lens": object_handler.safe_extract_attribute(camera_info_obj, "Lens"),
                "Filter": object_handler.safe_extract_attribute(
                    camera_info_obj, "Filter"
                ),
                "Fov": object_handler.safe_extract_attribute(
                    camera_info_obj,
                    "Fov",
                    convert_type="float",
                    float_precision=2,
                ),
                "Fps": object_handler.safe_extract_attribute(
                    self._camera.camera, "Fps", convert_type="float", float_precision=2
                ),
                "AveragePayload": object_handler.safe_extract_attribute(
                    self._camera.camera,
                    "AveragePayload",
                    convert_type="float",
                    float_precision=2,
                ),
                "FrameCount": object_handler.safe_extract_attribute(
                    self._camera.camera, "FrameCount", convert_type="int"
                ),
                "FrameRateIndex": object_handler.safe_extract_attribute(
                    self._camera.camera, "FrameRateIndex", convert_type="int"
                ),
                "LostImages": object_handler.safe_extract_attribute(
                    self._camera.camera, "LostImages", convert_type="int"
                ),
                "TimelapseReconnect": object_handler.safe_extract_attribute(
                    self._camera.camera, "TimelapseReconnect", convert_type="bool"
                ),
                "TimeoutCheckForHeartbeat": object_handler.safe_extract_attribute(
                    self._camera.camera, "TimeoutCheckForHeartbeat", convert_type="bool"
                ),
            }

            # Safely extract range information
            if hasattr(camera_info_obj, "Range") and camera_info_obj.Range is not None:
                range_obj = camera_info_obj.Range
                camera_info["Range"] = {
                    "Maximum": object_handler.safe_extract_attribute(
                        range_obj,
                        "Maximum",
                        convert_type="float",
                        float_precision=2,
                    ),
                    "Minimum": object_handler.safe_extract_attribute(
                        range_obj,
                        "Minimum",
                        convert_type="float",
                        float_precision=2,
                    ),
                }

            return camera_info
        except Exception as e:
            self.logger.warning(f"Error extracting camera information: {e}")
            return None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert camera information to dictionary format.

        Returns:
            Dictionary containing camera information
        """
        return {
            "Model": self.Model,
            "SerialNumber": self.SerialNumber,
            "Lens": self.Lens,
            "Filter": self.Filter,
            "Fov": self.Fov,
            "Range": self.Range,
            "Fps": self.Fps,
            "AveragePayload": self.AveragePayload,
            "FrameCount": self.FrameCount,
            "FrameRateIndex": self.FrameRateIndex,
            "LostImages": self.LostImages,
            "TimelapseReconnect": self.TimelapseReconnect,
            "TimeoutCheckForHeartbeat": self.TimeoutCheckForHeartbeat,
        }
