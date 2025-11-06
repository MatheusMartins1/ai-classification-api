"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

import os
from threading import Lock
from typing import Any, Dict, List, Optional

import clr

from config.settings import settings

# Add the path to the directory containing the compiled DLL
dll_path = os.path.join(settings.BASE_DIR, "ThermalCameraLibrary")

clr.AddReference(os.path.join(dll_path, "ThermalCamera.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Live.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Image.dll"))
clr.AddReference("System")
# clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Gigevision.dll"))

import Flir.Atlas.Image as Image  # type: ignore

# Import the necessary classes from the assembly
import Flir.Atlas.Live as live  # type: ignore

from utils import object_handler


class GPSInfo:
    """
    GPSInformation provides basic methods to handle a GPS information. More...
    """

    def __init__(self, _camera):
        """
        Initialize the GPSInfo class with a camera instance.
        """
        self._camera = _camera
        self.logger = _camera.logger
        self._service_lock = _camera.service_lock

        self._thermal_image = _camera.image_obj_thermal
        self._visual_image = _camera.image_obj_visual
        self.is_supported = True

        self.IsValid = None
        self.Altitude = None
        self.AltitudeRef = None
        self.Dop = None
        self.Latitude = None
        self.LatitudeRef = None
        self.Longitude = None
        self.LongitudeRef = None
        self.MapDatum = None
        self.Satellites = None
        self.Timestamp = None

        self._check_if_supported(self._thermal_image)

    def _check_if_supported(self, thermal_image: Optional[Any] = None):
        """
        Check if the GPS information is supported by the camera.
        """
        if thermal_image is None and self._thermal_image is None:
            self.is_supported = False
            return

        try:
            if thermal_image.GpsInformation is None:
                self.is_supported = False
                return
        except Exception as e:
            self.is_supported = False
            return

        self.is_supported = True

    def update_info(self, thermal_image: Optional[Any] = None) -> None:
        """
        Update the GPS information from the thermal image.
        """
        with self._service_lock:
            if thermal_image is None and self._thermal_image is None:
                return

            thermal_image = (
                thermal_image
                if isinstance(thermal_image, Image.ThermalImage)
                else self._thermal_image
            )

            gps_info = self.extract_gps_information(thermal_image)

            if gps_info is not None:
                self.IsValid = gps_info.get("IsValid")
                self.Altitude = gps_info.get("Altitude")
                self.AltitudeRef = gps_info.get("AltitudeRef")
                self.Dop = gps_info.get("Dop")
                self.Latitude = gps_info.get("Latitude")
                self.LatitudeRef = gps_info.get("LatitudeRef")
                self.Longitude = gps_info.get("Longitude")
                self.LongitudeRef = gps_info.get("LongitudeRef")
                self.MapDatum = gps_info.get("MapDatum")
                self.Satellites = gps_info.get("Satellites")
                self.Timestamp = gps_info.get("Timestamp")

    def set_gps_info(self, gps_info: Dict[str, Any]) -> None:
        # TODO: Implement this method
        pass

    def extract_gps_information(self, thermal_image: Any) -> Optional[Dict[str, Any]]:
        """
        Safely extract GPS information from thermal image.

        Args:
            thermal_image: Thermal image object

        Returns:
            GPS information dictionary or None if not available
        """
        self._check_if_supported(thermal_image)
        try:
            if thermal_image.GpsInformation is None:
                return None
        except Exception as e:
            self.logger.warning(f"Error accessing GpsInformation: {e}")
            return None

        try:
            gps_info = thermal_image.GpsInformation
            return {
                "IsValid": object_handler.safe_extract_attribute(
                    gps_info, "IsValid", convert_type="bool", default=False
                ),
                "Altitude": object_handler.safe_extract_attribute(
                    gps_info,
                    "Altitude",
                    convert_type="float",
                    float_precision=6,
                    default=0.0,
                ),
                "AltitudeRef": object_handler.safe_extract_attribute(
                    gps_info, "AltitudeRef", convert_type="int", default=0
                ),
                "Dop": object_handler.safe_extract_attribute(
                    gps_info,
                    "Dop",
                    convert_type="float",
                    float_precision=6,
                    default=0.0,
                ),
                "Latitude": object_handler.safe_extract_attribute(
                    gps_info,
                    "Latitude",
                    convert_type="float",
                    float_precision=6,
                    default=0.0,
                ),
                "LatitudeRef": object_handler.safe_extract_attribute(
                    gps_info, "LatitudeRef", convert_type="str", default=""
                ),
                "Longitude": object_handler.safe_extract_attribute(
                    gps_info,
                    "Longitude",
                    convert_type="float",
                    float_precision=6,
                    default=0.0,
                ),
                "LongitudeRef": object_handler.safe_extract_attribute(
                    gps_info, "LongitudeRef", convert_type="str", default=""
                ),
                "MapDatum": object_handler.safe_extract_attribute(
                    gps_info, "MapDatum", convert_type="str", default=""
                ),
                "Satellites": object_handler.safe_extract_attribute(
                    gps_info, "Satellites", convert_type="str", default=""
                ),
                "Timestamp": object_handler.safe_extract_attribute(
                    gps_info, "Timestamp", convert_type="int", default=0
                ),
            }
        except Exception as e:
            self.logger.warning(f"Error extracting GPS information: {e}")
            return None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert GPS information to dictionary format.

        Returns:
            Dictionary containing GPS information
        """
        return {
            "IsValid": self.IsValid,
            "Altitude": self.Altitude,
            "AltitudeRef": self.AltitudeRef,
            "Dop": self.Dop,
            "Latitude": self.Latitude,
            "LatitudeRef": self.LatitudeRef,
            "Longitude": self.Longitude,
            "LongitudeRef": self.LongitudeRef,
            "MapDatum": self.MapDatum,
            "Satellites": self.Satellites,
            "Timestamp": self.Timestamp,
        }
