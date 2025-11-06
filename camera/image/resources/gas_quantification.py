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


class GasQuantification:
    """
    GasQuantification provides basic methods to handle gas quantification data.
    """

    def __init__(self, _camera):
        """
        Initialize the GasQuantification class with a camera instance.
        """
        self._camera = _camera
        self.logger = _camera.logger
        self._service_lock = _camera.service_lock

        self._thermal_image = _camera.image_obj_thermal
        self._visual_image = _camera.image_obj_visual
        self.is_supported = True

        # Gas Quantification Result
        self.Flow = None
        self.Concentration = None

        # Gas Quantification Input
        self.IsValid = None
        self.AmbientTemperature = None
        self.Gas = None
        self.LeakType = None
        self.WindSpeed = None
        self.Distance = None
        self.ThresholdDeltaTemperature = None
        self.Emissive = None

        self._check_if_supported(self._thermal_image)

    def _check_if_supported(self, thermal_image: Optional[Any] = None):
        """
        Check if the gas quantification information is supported by the camera.
        """
        if thermal_image is None and self._thermal_image is None:
            self.is_supported = False
            return

        try:
            if (
                thermal_image.GasQuantificationResult is None
                and thermal_image.GasQuantificationInput is None
            ):
                self.is_supported = False
                return
        except Exception as e:
            self.is_supported = False
            return

        self.is_supported = True

    def update_info(self, thermal_image: Optional[Any] = None) -> None:
        """
        Update the gas quantification information from the thermal image.
        """
        with self._service_lock:
            if thermal_image is None and self._thermal_image is None:
                return

            thermal_image = (
                thermal_image
                if isinstance(thermal_image, Image.ThermalImage)
                else self._thermal_image
            )

            # Extract gas result and input
            gas_result = self.extract_gas_quantification_result(thermal_image)
            gas_input = self.extract_gas_quantification_input(thermal_image)

            if gas_result is not None:
                self.Flow = gas_result.get("Flow")
                self.Concentration = gas_result.get("Concentration")

            if gas_input is not None:
                self.IsValid = gas_input.get("IsValid")
                self.AmbientTemperature = gas_input.get("AmbientTemperature")
                self.Gas = gas_input.get("Gas")
                self.LeakType = gas_input.get("LeakType")
                self.WindSpeed = gas_input.get("WindSpeed")
                self.Distance = gas_input.get("Distance")
                self.ThresholdDeltaTemperature = gas_input.get(
                    "ThresholdDeltaTemperature"
                )
                self.Emissive = gas_input.get("Emissive")

    def extract_gas_quantification_result(
        self, thermal_image: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Safely extract gas quantification result from thermal image.

        Args:
            thermal_image: Thermal image object

        Returns:
            Gas quantification result dictionary or None if not available
        """
        self._check_if_supported(thermal_image)
        if not self.is_supported:
            return None

        try:
            gas_result = thermal_image.GasQuantificationResult
            return {
                "Flow": object_handler.safe_extract_attribute(
                    gas_result,
                    "Flow",
                    convert_type="float",
                    float_precision=2,
                ),
                "Concentration": object_handler.safe_extract_attribute(
                    gas_result,
                    "Concentration",
                    convert_type="float",
                    float_precision=2,
                ),
            }
        except Exception as e:
            self.logger.warning(f"Error extracting gas quantification result: {e}")
            return None

    def extract_gas_quantification_input(
        self, thermal_image: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Safely extract gas quantification input from thermal image.

        Args:
            thermal_image: Thermal image object

        Returns:
            Gas quantification input dictionary or None if not available
        """
        self._check_if_supported(thermal_image)
        if thermal_image.GasQuantificationInput is None:
            return None

        try:
            gas_input = thermal_image.GasQuantificationInput
            return {
                "IsValid": object_handler.safe_extract_attribute(
                    gas_input, "IsValid", convert_type="bool"
                ),
                "AmbientTemperature": object_handler.safe_extract_attribute(
                    gas_input,
                    "AmbientTemperature",
                    convert_type="float",
                    float_precision=2,
                ),
                "Gas": object_handler.safe_extract_attribute(gas_input, "Gas"),
                "LeakType": object_handler.safe_extract_attribute(
                    gas_input, "LeakType"
                ),
                "WindSpeed": object_handler.safe_extract_attribute(
                    gas_input, "WindSpeed"
                ),
                "Distance": object_handler.safe_extract_attribute(
                    gas_input, "Distance", convert_type="int"
                ),
                "ThresholdDeltaTemperature": object_handler.safe_extract_attribute(
                    gas_input,
                    "ThresholdDeltaTemperature",
                    convert_type="float",
                    float_precision=2,
                ),
                "Emissive": object_handler.safe_extract_attribute(
                    gas_input, "Emissive", convert_type="bool"
                ),
            }
        except Exception as e:
            self.logger.warning(f"Error extracting gas quantification input: {e}")
            return None

    def set_gas_quantification_input(self, gas_input: Dict[str, Any]) -> None:
        # TODO: Implement this method
        pass

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert gas quantification information to dictionary format.

        Returns:
            Dictionary containing gas quantification information
        """
        return {
            "Result": {
                "Flow": self.Flow,
                "Concentration": self.Concentration,
            },
            "Input": {
                "IsValid": self.IsValid,
                "AmbientTemperature": self.AmbientTemperature,
                "Gas": self.Gas,
                "LeakType": self.LeakType,
                "WindSpeed": self.WindSpeed,
                "Distance": self.Distance,
                "ThresholdDeltaTemperature": self.ThresholdDeltaTemperature,
                "Emissive": self.Emissive,
            },
        }
