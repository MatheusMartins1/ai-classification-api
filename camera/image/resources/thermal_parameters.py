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


class ThermalParameters:
    """
    ThermalParameters provides basic methods to handle thermal parameters.
    """

    def __init__(self, _camera):
        """
        Initialize the ThermalParameters class with a camera instance.
        """
        self._camera = _camera
        self.logger = _camera.logger
        self._service_lock = _camera.service_lock

        self._thermal_image = _camera.image_obj_thermal
        self._visual_image = _camera.image_obj_visual
        self.is_supported = True

        self.AtmosphericTemperature = None
        self.Distance = None
        self.Emissivity = None
        self.ExternalOpticsTemperature = None
        self.ExternalOpticsTransmission = None
        self.ReferenceTemperature = None
        self.ReflectedTemperature = None
        self.RelativeHumidity = None
        self.Transmission = None

        self._check_if_supported(self._thermal_image)

    def _check_if_supported(self, thermal_image: Optional[Any] = None):
        """
        Check if the thermal parameters are supported by the camera.
        """
        if thermal_image is None and self._thermal_image is None:
            self.is_supported = False
            return

        try:
            if thermal_image.ThermalParameters is None:
                self.is_supported = False
                return
        except Exception as e:
            self.is_supported = False
            return

        self.is_supported = True

    def update_info(self, thermal_image: Optional[Any] = None) -> None:
        """
        Update the thermal parameters from the thermal image.
        """
        with self._service_lock:
            if thermal_image is None and self._thermal_image is None:
                return

            thermal_image = (
                thermal_image
                if isinstance(thermal_image, Image.ThermalImage)
                else self._thermal_image
            )

            thermal_params = self.extract_thermal_parameters(thermal_image)

            if thermal_params is not None:
                self.AtmosphericTemperature = thermal_params.get(
                    "AtmosphericTemperature"
                )
                self.Distance = thermal_params.get("Distance")
                self.Emissivity = thermal_params.get("Emissivity")
                self.ExternalOpticsTemperature = thermal_params.get(
                    "ExternalOpticsTemperature"
                )
                self.ExternalOpticsTransmission = thermal_params.get(
                    "ExternalOpticsTransmission"
                )
                self.ReferenceTemperature = thermal_params.get("ReferenceTemperature")
                self.ReflectedTemperature = thermal_params.get("ReflectedTemperature")
                self.RelativeHumidity = thermal_params.get("RelativeHumidity")
                self.Transmission = thermal_params.get("Transmission")

    def extract_thermal_parameters(
        self, thermal_image: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Safely extract thermal parameters from thermal image.

        Args:
            thermal_image: Thermal image object

        Returns:
            Thermal parameters dictionary or None if not available
        """
        self._check_if_supported(thermal_image)
        if thermal_image.ThermalParameters is None:
            return None

        try:
            thermal_params = thermal_image.ThermalParameters
            return {
                "AtmosphericTemperature": object_handler.safe_extract_attribute(
                    thermal_params,
                    "AtmosphericTemperature",
                    convert_type="float",
                    float_precision=1,
                ),
                "Distance": object_handler.safe_extract_attribute(
                    thermal_params, "Distance", convert_type="float", float_precision=1
                ),
                "Emissivity": object_handler.safe_extract_attribute(
                    thermal_params,
                    "Emissivity",
                    convert_type="float",
                    float_precision=1,
                ),
                "ExternalOpticsTemperature": object_handler.safe_extract_attribute(
                    thermal_params,
                    "ExternalOpticsTemperature",
                    convert_type="float",
                    float_precision=1,
                ),
                "ExternalOpticsTransmission": object_handler.safe_extract_attribute(
                    thermal_params,
                    "ExternalOpticsTransmission",
                    convert_type="float",
                    float_precision=1,
                ),
                "ReferenceTemperature": object_handler.safe_extract_attribute(
                    thermal_params,
                    "ReferenceTemperature",
                    convert_type="float",
                    float_precision=1,
                ),
                "ReflectedTemperature": object_handler.safe_extract_attribute(
                    thermal_params,
                    "ReflectedTemperature",
                    convert_type="float",
                    float_precision=1,
                ),
                "RelativeHumidity": object_handler.safe_extract_attribute(
                    thermal_params,
                    "RelativeHumidity",
                    convert_type="float",
                    float_precision=1,
                ),
                "Transmission": object_handler.safe_extract_attribute(
                    thermal_params,
                    "Transmission",
                    convert_type="float",
                    float_precision=1,
                ),
            }
        except Exception as e:
            self.logger.warning(f"Error extracting thermal parameters: {e}")
            return None

    def set_parameters(
        self,
        atmospheric_temperature: Optional[float] = None,
        distance: Optional[float] = None,
        emissivity: Optional[float] = None,
        external_optics_temperature: Optional[float] = None,
        external_optics_transmission: Optional[float] = None,
        reference_temperature: Optional[float] = None,
        reflected_temperature: Optional[float] = None,
        relative_humidity: Optional[float] = None,
        transmission: Optional[float] = None,
    ):
        """
        Set thermal parameters.

        Args:
            atmospheric_temperature: Atmospheric temperature
            distance: Distance
            emissivity: Emissivity
            external_optics_temperature: External optics temperature
            external_optics_transmission: External optics transmission
            reference_temperature: Reference temperature
            reflected_temperature: Reflected temperature
            relative_humidity: Relative humidity
            transmission: Transmission
        """
        try:
            if atmospheric_temperature:
                self._thermal_image.ThermalParameters.AtmosphericTemperature = float(
                    atmospheric_temperature
                )
        except Exception as e:
            self.logger.warning(f"Error setting AtmosphericTemperature: {e}")

        try:
            if distance:
                self._thermal_image.ThermalParameters.Distance = float(distance)
        except Exception as e:
            self.logger.warning(f"Error setting Distance: {e}")

        try:
            if emissivity:
                self._thermal_image.ThermalParameters.Emissivity = float(emissivity)
        except Exception as e:
            self.logger.warning(f"Error setting Emissivity: {e}")

        try:
            if external_optics_temperature:
                self._thermal_image.ThermalParameters.ExternalOpticsTemperature = float(
                    external_optics_temperature
                )
        except Exception as e:
            self.logger.warning(f"Error setting ExternalOpticsTemperature: {e}")

        try:
            if external_optics_transmission:
                self._thermal_image.ThermalParameters.ExternalOpticsTransmission = (
                    float(external_optics_transmission)
                )
        except Exception as e:
            self.logger.warning(f"Error setting ExternalOpticsTransmission: {e}")

        try:
            if reference_temperature:
                self._thermal_image.ThermalParameters.ReferenceTemperature = float(
                    reference_temperature
                )
        except Exception as e:
            self.logger.warning(f"Error setting ReferenceTemperature: {e}")

        try:
            if reflected_temperature:
                self._thermal_image.ThermalParameters.ReflectedTemperature = float(
                    reflected_temperature
                )
        except Exception as e:
            self.logger.warning(f"Error setting ReflectedTemperature: {e}")

        try:
            if relative_humidity:
                self._thermal_image.ThermalParameters.RelativeHumidity = float(
                    relative_humidity
                )
        except Exception as e:
            self.logger.warning(f"Error setting RelativeHumidity: {e}")

        try:
            if transmission:
                self._thermal_image.ThermalParameters.Transmission = float(transmission)
        except Exception as e:
            self.logger.warning(f"Error setting Transmission: {e}")

        self.update_info()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert thermal parameters to dictionary format.

        Returns:
            Dictionary containing thermal parameters
        """
        return {
            "AtmosphericTemperature": self.AtmosphericTemperature,
            "Distance": self.Distance,
            "Emissivity": self.Emissivity,
            "ExternalOpticsTemperature": self.ExternalOpticsTemperature,
            "ExternalOpticsTransmission": self.ExternalOpticsTransmission,
            "ReferenceTemperature": self.ReferenceTemperature,
            "ReflectedTemperature": self.ReflectedTemperature,
            "RelativeHumidity": self.RelativeHumidity,
            "Transmission": self.Transmission,
        }
