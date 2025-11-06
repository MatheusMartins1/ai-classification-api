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

# Import the necessary classes from the assembly
import Flir.Atlas.Image as Image  # type: ignore


class HumidityAlarmManager:
    """
    The humidity isotherm can detect areas where there is a risk of mold growing, or where there is a risk of the humidity falling out as liquid water (i.e., the dew point).
    """

    def __init__(self, alarm: Image.Alarms.HumidityAlarm):
        """
        Initialize the HumidityAlarmManager class with a Flir HumidityAlarm instance.

        :param alarm: Flir HumidityAlarm instance
        """
        self._alarm = alarm

    @property
    def atmospheric_temperature(self) -> float:
        """
        Gets or sets the atmospheric temperature.

        :return: Atmospheric temperature
        """
        return self._alarm.AtmosphericTemperature

    @atmospheric_temperature.setter
    def atmospheric_temperature(self, value: float):
        self._alarm.AtmosphericTemperature = value

    @property
    def relative_air_humidity(self) -> float:
        """
        Gets or sets the relative air humidity.

        :return: Relative air humidity
        """
        return self._alarm.RelativeAirHumidity

    @relative_air_humidity.setter
    def relative_air_humidity(self, value: float):
        if not 0.0 <= value <= 1.0:
            raise ValueError("The value must be in the range 0.0 - 1.0")
        self._alarm.RelativeAirHumidity = value

    @property
    def relative_humidity_alarm_level(self) -> float:
        """
        Gets or sets the relative humidity alarms level.

        :return: Relative humidity alarms level
        """
        return self._alarm.RelativeHumidityAlarmLevel

    @relative_humidity_alarm_level.setter
    def relative_humidity_alarm_level(self, value: float):
        if not 0.0 <= value <= 1.0:
            raise ValueError("The value must be in the range 0.0 - 1.0")
        self._alarm.RelativeHumidityAlarmLevel = value

    @property
    def isotherm(self) -> str:
        """
        Gets or sets the isotherm identity.

        :return: Isotherm identity
        """
        return self._alarm.Isotherm

    @isotherm.setter
    def isotherm(self, value: str):
        self._alarm.Isotherm = value

    @property
    def measurement_rectangle(self) -> str:
        """
        Gets or sets the measurement rectangle.

        :return: Measurement rectangle
        """
        return self._alarm.MeasurementRectangle

    @measurement_rectangle.setter
    def measurement_rectangle(self, value: str):
        self._alarm.MeasurementRectangle = value

    @property
    def iso_coverage_threshold(self) -> float:
        """
        Gets or sets the isotherm coverage threshold.

        :return: Isotherm coverage threshold
        """
        return self._alarm.IsoCoverageThreshold

    @iso_coverage_threshold.setter
    def iso_coverage_threshold(self, value: float):
        self._alarm.IsoCoverageThreshold = value

    def calculate_relative_humidity_alarm_temperature(self) -> float:
        """
        Calculates the relative humidity alarms temperature.

        :return: The relative humidity alarms temperature in Kelvin.
        """
        return self._alarm.CalculateRelativeHumidityAlarmTemperature()

    @staticmethod
    def calculate_relative_humidity_alarm_temperature_static(
        factor: float, atm_temp: float, rel_hum: float
    ) -> float:
        """
        Calculates the relative humidity alarms temperature.

        :param factor: The factor (0.0 - 1.0).
        :param atm_temp: The air temperature.
        :param rel_hum: Relative humidity.
        :return: The relative humidity alarms temperature in Kelvin.
        """
        return Image.Alarms.HumidityAlarm.CalculateRelativeHumidityAlarmTemperature(
            factor, atm_temp, rel_hum
        )
