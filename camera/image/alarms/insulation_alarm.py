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


class InsulationAlarmManager:
    """
    The insulation alarms can detect areas where there may be an insulation deficiency in the building.
    """

    def __init__(self, alarm: Image.Alarms.InsulationAlarm):
        """
        Initialize the InsulationAlarmManager class with a Flir InsulationAlarm instance.

        :param alarm: Flir InsulationAlarm instance
        """
        self._alarm = alarm

    @property
    def indoor_air_temperature(self) -> float:
        """
        Gets or sets the indoor air temperature.

        :return: Indoor air temperature
        """
        return self._alarm.IndoorAirTemperature

    @indoor_air_temperature.setter
    def indoor_air_temperature(self, value: float):
        self._alarm.IndoorAirTemperature = value

    @property
    def insulation_factor(self) -> float:
        """
        Gets or sets the insulation factor.

        :return: Insulation factor
        """
        return self._alarm.InsulationFactor

    @insulation_factor.setter
    def insulation_factor(self, value: float):
        self._alarm.InsulationFactor = value

    @property
    def outdoor_air_temperature(self) -> float:
        """
        Gets or sets the outdoor air temperature.

        :return: Outdoor air temperature
        """
        return self._alarm.OutdoorAirTemperature

    @outdoor_air_temperature.setter
    def outdoor_air_temperature(self, value: float):
        self._alarm.OutdoorAirTemperature = value

    @property
    def reserved(self) -> int:
        """
        Gets or sets the reserved.

        :return: Reserved
        """
        return self._alarm.Reserved

    @reserved.setter
    def reserved(self, value: int):
        self._alarm.Reserved = value

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

    def insulation_limit(self) -> float:
        """
        Calculates the alarms insulation limit.

        :return: The alarms insulation limit in Kelvin.
        """
        return self._alarm.InsulationLimit()

    @staticmethod
    def insulation_limit_static(
        factor: int, indoor_temp: float, outdoor_temp: float
    ) -> float:
        """
        Calculates the insulation limit.

        :param factor: The factor.
        :param indoor_temp: The indoor temperature.
        :param outdoor_temp: The outdoor temperature.
        :return: The insulation limit in Kelvin.
        """
        return Image.Alarms.InsulationAlarm.InsulationLimit(
            factor, indoor_temp, outdoor_temp
        )
