import numpy as np
import statistics
import pandas as pd

def generate_delta(temp1: float, temp2: float) -> float:
    """
    Generate the delta between two temperatures.
    """
    #FIXME: Corrigir o cálculo do Delta-T, use numpy
    return temp2 - temp1

def get_max_from_temperature_array(temperature_array: list[float]) -> float:
    """
    Get the max temperature from a temperature array.
    """
    return max(temperature_array)

def get_min_from_temperature_array(temperature_array: list[float]) -> float:
    """
    Get the min temperature from a temperature array.
    """
    return min(temperature_array)

def get_average_from_temperature_array(temperature_array: list[float]) -> float:
    """
    Get the average temperature from a temperature array.
    """
    #TODO: Fix
    return sum(temperature_array) / len(temperature_array)

def get_median_from_temperature_array(temperature_array: list[float]) -> float:
    """
    Get the median temperature from a temperature array.
    """
    #TODO: Fix
    return statistics.median(temperature_array)

def get_mta() -> float:
    """
    Get the MTA (Maximum Allowable Temperature)
    """
    #TODO: Implement logic to get MTA based on context
    return 100.0

def convert_temperature_unit(
        self, temperature, unit_from="Kelvin", unit_to="Celsius"
    ):
        """
        Convert the temperature from one unit to another.

        Args:
            temperature: The temperature to convert.
            unit_from: The unit to convert from.
            unit_to: The unit to convert to.

        Returns:
            The converted temperature.
        """
        if unit_from == unit_to:
            return temperature

        # Convert from the source unit to Kelvin
        if unit_from == "Celsius":
            temperature_in_kelvin = temperature + 273.15
        elif unit_from == "Fahrenheit":
            temperature_in_kelvin = (temperature - 32) * 5 / 9 + 273.15
        elif unit_from == "Kelvin":
            temperature_in_kelvin = temperature
        else:
            raise ValueError(f"Unsupported temperature unit: {unit_from}")

        # Convert from Kelvin to the target unit
        if unit_to == "Celsius":
            return temperature_in_kelvin - 273.15
        elif unit_to == "Fahrenheit":
            return (temperature_in_kelvin - 273.15) * 9 / 5 + 32
        elif unit_to == "Kelvin":
            return temperature_in_kelvin
        else:
            raise ValueError(f"Unsupported temperature unit: {unit_to}")
