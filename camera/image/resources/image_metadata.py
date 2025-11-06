"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

import datetime
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


class ImageMetadata:
    """
    ImageMetadata provides basic methods to handle image metadata.
    """

    def __init__(self, _camera):
        """
        Initialize the ImageMetadata class with a camera instance.
        """
        self._camera = _camera
        self.logger = _camera.logger
        self._service_lock = _camera.service_lock

        self._thermal_image = _camera.image_obj_thermal
        self._visual_image = _camera.image_obj_visual
        self.is_supported = True

        self.FileName = None
        self.Height = None
        self.Width = None
        self.FrameCount = None
        self.TemperatureUnit = None
        self.DistanceUnit = None
        self.ColorDistribution = None
        self.Description = None
        self.DateTime = None
        self.DateTaken = None
        self.ContainsUltraMaxData = None
        self.MaxSignalValue = None
        self.MinSignalValue = None
        self.OverflowSignalValue = None
        self.UnderflowSignalValue = None
        self.Precision = None

        # TODO: implement this atributtes
        self.Size = None
        self.IsSilent = None
        self.IsDisposed = None
        self.Version = None

        self._check_if_supported(self._thermal_image)

    def _check_if_supported(self, thermal_image: Optional[Any] = None):
        """
        Check if the image metadata is supported by the camera.
        """
        if thermal_image is None and self._thermal_image is None:
            self.is_supported = False
            return

        try:
            # Image metadata is always available for thermal images
            if thermal_image is None:
                self.is_supported = False
                return
        except Exception as e:
            self.is_supported = False
            return

        self.is_supported = True

    def update_info(self, thermal_image: Optional[Any] = None) -> None:
        """
        Update the image metadata from the thermal image.
        """
        with self._service_lock:
            if thermal_image is None and self._thermal_image is None:
                return

            thermal_image = (
                thermal_image
                if isinstance(thermal_image, Image.ThermalImage)
                else self._thermal_image
            )

            metadata = self.extract_image_metadata(thermal_image)

            if metadata is not None:
                self.FileName = metadata.get("FileName")
                self.Height = metadata.get("Height")
                self.Width = metadata.get("Width")
                self.FrameCount = metadata.get("FrameCount")
                self.TemperatureUnit = metadata.get("TemperatureUnit")
                self.DistanceUnit = metadata.get("DistanceUnit")
                self.ColorDistribution = metadata.get("ColorDistribution")
                self.Description = metadata.get("Description")
                self.DateTime = metadata.get("DateTime")
                self.DateTaken = metadata.get("DateTaken")
                self.ContainsUltraMaxData = metadata.get("ContainsUltraMaxData")
                self.MaxSignalValue = metadata.get("MaxSignalValue")
                self.MinSignalValue = metadata.get("MinSignalValue")
                self.OverflowSignalValue = metadata.get("OverflowSignalValue")
                self.UnderflowSignalValue = metadata.get("UnderflowSignalValue")
                self.Precision = metadata.get("Precision")

            self.logger.debug(f"Image metadata updated")

    def extract_image_metadata(self, thermal_image: Any) -> Dict[str, Any]:
        """
        Extract basic image metadata safely.

        Args:
            thermal_image: Thermal image object

        Returns:
            Image metadata dictionary
        """
        self._check_if_supported(thermal_image)

        TemperatureUnit = object_handler.safe_extract_attribute(
            thermal_image, "TemperatureUnit"
        )
        DistanceUnit = object_handler.safe_extract_attribute(
            thermal_image, "DistanceUnit"
        )
        ColorDistribution = object_handler.safe_extract_attribute(
            thermal_image, "ColorDistribution"
        )
        DateTime = object_handler.safe_extract_attribute(thermal_image, "DateTime")
        DateTaken = object_handler.safe_extract_attribute(thermal_image, "DateTaken")

        try:
            DateTime = (
                datetime.datetime(
                    self._thermal_image.DateTime.Year,
                    self._thermal_image.DateTime.Month,
                    self._thermal_image.DateTime.Day,
                    self._thermal_image.DateTime.Hour,
                    self._thermal_image.DateTime.Minute,
                    self._thermal_image.DateTime.Second,
                    microsecond=self._thermal_image.DateTime.Millisecond * 1000,
                )
                if not DateTime
                else DateTime
            )
        except Exception as e:
            self.logger.warning(f"Error parsing DateTime: {e}")
            DateTime = None

        try:
            DateTaken = (
                datetime.datetime(
                    self._thermal_image.DateTaken.Year,
                    self._thermal_image.DateTaken.Month,
                    self._thermal_image.DateTaken.Day,
                    self._thermal_image.DateTaken.Hour,
                    self._thermal_image.DateTaken.Minute,
                    self._thermal_image.DateTaken.Second,
                    microsecond=self._thermal_image.DateTaken.Millisecond * 1000,
                )
                if not DateTaken
                else DateTaken
            )
        except Exception as e:
            self.logger.warning(f"Error parsing DateTime: {e}")
            DateTaken = None

        metadata_dict = {
            "FileName": object_handler.safe_extract_attribute(thermal_image, "Title"),
            "Height": object_handler.safe_extract_attribute(
                thermal_image, "Height", convert_type="int"
            ),
            "Width": object_handler.safe_extract_attribute(
                thermal_image, "Width", convert_type="int"
            ),
            # "FrameCount": object_handler.safe_extract_attribute(thermal_image, "Count"),
            "TemperatureUnit": self._TemperatureUnitEnum.get(
                TemperatureUnit, TemperatureUnit
            ),
            "DistanceUnit": self._DistanceUnitEnum.get(DistanceUnit, DistanceUnit),
            "ColorDistribution": self._ColorDistributionEnum.get(
                ColorDistribution, ColorDistribution
            ),
            "Description": object_handler.safe_extract_attribute(
                thermal_image, "Description"
            ),
            "DateTime": DateTime,
            "DateTaken": DateTaken,
            "ContainsUltraMaxData": object_handler.safe_extract_attribute(
                thermal_image, "ContainsUltraMaxData"
            ),
            "MaxSignalValue": object_handler.safe_extract_attribute(
                thermal_image, "MaxSignalValue", convert_type="int"
            ),
            "MinSignalValue": object_handler.safe_extract_attribute(
                thermal_image, "MinSignalValue", convert_type="int"
            ),
            "OverflowSignalValue": object_handler.safe_extract_attribute(
                thermal_image, "OverflowSignalValue", convert_type="int"
            ),
            "UnderflowSignalValue": object_handler.safe_extract_attribute(
                thermal_image, "UnderflowSignalValue", convert_type="int"
            ),
            "Precision": object_handler.safe_extract_attribute(
                thermal_image, "Precision", convert_type="int"
            ),
        }

        return metadata_dict

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert image metadata to dictionary format.

        Returns:
            Dictionary containing image metadata
        """
        return {
            "FileName": self.FileName,
            "Height": self.Height,
            "Width": self.Width,
            "FrameCount": self.FrameCount,
            "TemperatureUnit": self.TemperatureUnit,
            "DistanceUnit": self.DistanceUnit,
            "ColorDistribution": self.ColorDistribution,
            "Description": self.Description,
            "DateTime": self.DateTime,
            "DateTaken": self.DateTaken,
            "ContainsUltraMaxData": self.ContainsUltraMaxData,
            "MaxSignalValue": self.MaxSignalValue,
            "MinSignalValue": self.MinSignalValue,
            "OverflowSignalValue": self.OverflowSignalValue,
            "UnderflowSignalValue": self.UnderflowSignalValue,
            "Precision": self.Precision,
        }

    _TemperatureUnitEnum = {0: "Celsius", 1: "Fahrenheit", 2: "Kelvin", 3: "Signal"}
    _DistanceUnitEnum = {0: "Meter", 1: "Feet"}
    _ColorDistributionEnum = {
        0: "TemperatureLinear",
        1: "HistogramEqualization",
        2: "SignalLinear",
        3: "DigitalDetailEnhancement",
        4: "Ade",
        5: "Entropy",
        6: "PlateauHistogramEq",
        7: "GuidedFilterDDE",
        8: "Fsx",
    }
