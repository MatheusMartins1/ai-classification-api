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


class StatisticsInfo:
    """
    StatisticsInfo provides basic methods to handle statistics information.
    """

    def __init__(self, _camera):
        """
        Initialize the StatisticsInfo class with a camera instance.
        """
        self._camera = _camera
        self.logger = _camera.logger
        self._service_lock = _camera.service_lock

        self._thermal_image = _camera.image_obj_thermal
        self._visual_image = _camera.image_obj_visual
        self.is_supported = True

        self.Min = None
        self.Max = None
        self.Average = None
        self.StandardDeviation = None
        self.ColdSpot = None
        self.HotSpot = None

        self._check_if_supported(self._thermal_image)

    def _check_if_supported(self, thermal_image: Optional[Any] = None):
        """
        Check if the statistics information is supported by the camera.
        """
        if thermal_image is None and self._thermal_image is None:
            self.is_supported = False
            return

        try:
            if thermal_image.Statistics is None:
                self.is_supported = False
                return
        except Exception as e:
            self.is_supported = False
            return

        self.is_supported = True

    def update_info(self, thermal_image: Optional[Any] = None) -> None:
        """
        Update the statistics information from the thermal image.
        """
        with self._service_lock:
            if thermal_image is None and self._thermal_image is None:
                return

            thermal_image = (
                thermal_image
                if isinstance(thermal_image, Image.ThermalImage)
                else self._thermal_image
            )

            statistics_info = self.extract_statistics_information(thermal_image)

            if statistics_info is not None:
                self.Min = statistics_info.get("Min")
                self.Max = statistics_info.get("Max")
                self.Average = statistics_info.get("Average")
                self.StandardDeviation = statistics_info.get("StandardDeviation")
                self.ColdSpot = statistics_info.get("ColdSpot")
                self.HotSpot = statistics_info.get("HotSpot")

    def extract_statistics_information(
        self, thermal_image: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Safely extract statistics information from thermal image.

        Args:
            thermal_image: Thermal image object

        Returns:
            Statistics information dictionary or None if not available
        """
        self._check_if_supported(thermal_image)
        if thermal_image.Statistics is None:
            return None

        statistics_info = {}

        try:
            statistics = thermal_image.Statistics

            statistics_info = {
                "Min": object_handler.safe_extract_attribute(
                    statistics.Min, "Value", convert_type="float", float_precision=2
                ),
                "Max": object_handler.safe_extract_attribute(
                    statistics.Max, "Value", convert_type="float", float_precision=2
                ),
                "Average": object_handler.safe_extract_attribute(
                    statistics.Average, "Value", convert_type="float", float_precision=2
                ),
                "StandardDeviation": object_handler.safe_extract_attribute(
                    statistics.StandardDeviation,
                    "Value",
                    convert_type="float",
                    float_precision=2,
                ),
            }
        except Exception as e:
            self.logger.warning(f"Error extracting statistics information: {e}")
            return None

        try:
            ColdSpot = {
                "x": object_handler.safe_extract_attribute(
                    statistics.ColdSpot, "X", convert_type="int"
                ),
                "y": object_handler.safe_extract_attribute(
                    statistics.ColdSpot, "Y", convert_type="int"
                ),
            }
            statistics_info["ColdSpot"] = ColdSpot
        except Exception as e:
            self.logger.warning(f"Error extracting cold spot information: {e}")

        try:
            HotSpot = {
                "x": object_handler.safe_extract_attribute(
                    statistics.HotSpot, "X", convert_type="int"
                ),
                "y": object_handler.safe_extract_attribute(
                    statistics.HotSpot, "Y", convert_type="int"
                ),
            }
            statistics_info["HotSpot"] = HotSpot
        except Exception as e:
            self.logger.warning(f"Error extracting hot spot information: {e}")

        return statistics_info

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert statistics information to dictionary format.

        Returns:
            Dictionary containing statistics information
        """
        return {
            "Min": self.Min,
            "Max": self.Max,
            "Average": self.Average,
            "StandardDeviation": self.StandardDeviation,
            "ColdSpot": self.ColdSpot,
            "HotSpot": self.HotSpot,
        }
