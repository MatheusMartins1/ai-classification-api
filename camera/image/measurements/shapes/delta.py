"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

import os
from typing import Optional

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

from camera.image.measurements.measurement_shape import MeasurementShapeManager


class MeasurementDeltaManager(MeasurementShapeManager):
    """
    Holds the measurement delta functionality.

    Reference:
        https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/class_flir_1_1_atlas_1_1_image_1_1_measurements_1_1_measurement_delta.html
    """

    def __init__(self, _camera):
        """
        Initialize the MeasurementDeltaManager class with a camera instance.
        """
        super().__init__(_camera)
        self._camera = self._camera
        self._logger = _camera.logger
        self._image = _camera.image_obj_thermal
        self._visual_image = _camera.image_obj_visual

        # Initialize properties
        self._value_member1 = None
        self._value_member2 = None
        self._measurement1 = None
        self._measurement2 = None
        self._value = None

        # Load initial settings
        self.initialize_settings()

    def initialize_settings(self):
        """
        Initialize all settings by calling the respective get methods.
        """
        self._value_member1 = self.get_value_member1()
        self._value_member2 = self.get_value_member2()
        self._measurement1 = self.get_measurement1()
        self._measurement2 = self.get_measurement2()
        self._value = self.get_value()

    @property
    def value_member1(self) -> Optional[Image.Measurements.ValueMember]:
        """
        Get the first ValueMember.

        Returns:
            Optional[Image.Measurements.ValueMember]: The first ValueMember.
        """
        with self._service_lock:
            return self._value_member1

    @value_member1.setter
    def value_member1(self, value: Image.Measurements.ValueMember):
        """
        Set the first ValueMember.

        Args:
            value (Image.Measurements.ValueMember): The first ValueMember.
        """
        with self._service_lock:
            self._value_member1 = value
            self.set_value_member1(value)

    def get_value_member1(self) -> Optional[Image.Measurements.ValueMember]:
        """
        Get the first ValueMember.

        Returns:
            Optional[Image.Measurements.ValueMember]: The first ValueMember.
        """
        try:
            return self._image.Measurements.MeasurementDelta.ValueMember1
        except Exception as e:
            self._logger.error(f"Failed to get value member 1: {e}")
            return None

    def set_value_member1(self, value: Image.Measurements.ValueMember):
        """
        Set the first ValueMember.

        Args:
            value (Image.Measurements.ValueMember): The first ValueMember.
        """
        try:
            self._image.Measurements.MeasurementDelta.ValueMember1 = value
            self._logger.info("Value member 1 set.")
        except Exception as e:
            self._logger.error(f"Failed to set value member 1: {e}")

    @property
    def value_member2(self) -> Optional[Image.Measurements.ValueMember]:
        """
        Get the second ValueMember.

        Returns:
            Optional[Image.Measurements.ValueMember]: The second ValueMember.
        """
        with self._service_lock:
            return self._value_member2

    @value_member2.setter
    def value_member2(self, value: Image.Measurements.ValueMember):
        """
        Set the second ValueMember.

        Args:
            value (Image.Measurements.ValueMember): The second ValueMember.
        """
        with self._service_lock:
            self._value_member2 = value
            self.set_value_member2(value)

    def get_value_member2(self) -> Optional[Image.Measurements.ValueMember]:
        """
        Get the second ValueMember.

        Returns:
            Optional[Image.Measurements.ValueMember]: The second ValueMember.
        """
        try:
            return self._image.Measurements.MeasurementDelta.ValueMember2
        except Exception as e:
            self._logger.error(f"Failed to get value member 2: {e}")
            return None

    def set_value_member2(self, value: Image.Measurements.ValueMember):
        """
        Set the second ValueMember.

        Args:
            value (Image.Measurements.ValueMember): The second ValueMember.
        """
        try:
            self._image.Measurements.MeasurementDelta.ValueMember2 = value
            self._logger.info("Value member 2 set.")
        except Exception as e:
            self._logger.error(f"Failed to set value member 2: {e}")

    @property
    def measurement1(self) -> Optional[str]:
        """
        Get the first measurement.

        Returns:
            Optional[str]: The first measurement.
        """
        with self._service_lock:
            return self._measurement1

    def get_measurement1(self) -> Optional[str]:
        """
        Get the first measurement.

        Returns:
            Optional[str]: The first measurement.
        """
        try:
            return self._image.Measurements.MeasurementDelta.Measurement1
        except Exception as e:
            self._logger.error(f"Failed to get measurement 1: {e}")
            return None

    @property
    def measurement2(self) -> Optional[str]:
        """
        Get the second measurement.

        Returns:
            Optional[str]: The second measurement.
        """
        with self._service_lock:
            return self._measurement2

    def get_measurement2(self) -> Optional[str]:
        """
        Get the second measurement.

        Returns:
            Optional[str]: The second measurement.
        """
        try:
            return self._image.Measurements.MeasurementDelta.Measurement2
        except Exception as e:
            self._logger.error(f"Failed to get measurement 2: {e}")
            return None

    @property
    def value(self) -> Optional[Image.Measurements.ThermalValue]:
        """
        Get the value of this Delta.

        Returns:
            Optional[Image.Measurements.ThermalValue]: The value of this Delta.
        """
        with self._service_lock:
            return self._value

    def get_value(self) -> Optional[Image.Measurements.ThermalValue]:
        """
        Get the value of this Delta.

        Returns:
            Optional[Image.Measurements.ThermalValue]: The value of this Delta.
        """
        try:
            return self._image.Measurements.MeasurementDelta.Value
        except Exception as e:
            self._logger.error(f"Failed to get value: {e}")
            return None

    def is_equal(self, source: Image.Measurements.MeasurementShape) -> bool:
        """
        Compares two measurements.

        Args:
            source (Image.Measurements.MeasurementShape): The source MeasurementShape to compare with.

        Returns:
            bool: True if equal settings, otherwise False.
        """
        try:
            return self._image.Measurements.MeasurementDelta.IsEqual(source)
        except Exception as e:
            self._logger.error(f"Failed to compare measurements: {e}")
            return False

    def to_string(self) -> dict:
        """
        Return all properties in JSON format.

        Returns:
            dict: JSON string of all properties.
        """
        return {
            "value_member1": str(self.value_member1),
            "value_member2": str(self.value_member2),
            "measurement1": self.measurement1,
            "measurement2": self.measurement2,
            "value": str(self.value),
        }
