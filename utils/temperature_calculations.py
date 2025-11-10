"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Temperature calculation utilities for thermal image analysis.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

from typing import Union

import numpy as np  # type: ignore


def generate_delta(temp1: float, temp2: float) -> float:
    """
    Generate the delta between two temperatures using numpy.

    Args:
        temp1: First temperature value
        temp2: Second temperature value

    Returns:
        Delta temperature (temp2 - temp1)
    """
    # TODO: Check if this calculation is correct
    return float(np.subtract(temp2, temp1))


def get_max_from_temperature_array(
    temperature_array: Union[list[float], np.ndarray],
) -> float:
    """
    Get the max temperature from a temperature array using numpy.

    Args:
        temperature_array: Array of temperature values

    Returns:
        Maximum temperature value
    """
    return float(np.max(temperature_array))


def get_min_from_temperature_array(
    temperature_array: Union[list[float], np.ndarray],
) -> float:
    """
    Get the min temperature from a temperature array using numpy.

    Args:
        temperature_array: Array of temperature values

    Returns:
        Minimum temperature value
    """
    return float(np.min(temperature_array))


def get_average_from_temperature_array(
    temperature_array: Union[list[float], np.ndarray],
) -> float:
    """
    Get the average temperature from a temperature array using numpy.

    Args:
        temperature_array: Array of temperature values

    Returns:
        Average temperature value
    """
    return float(np.mean(temperature_array))


def get_median_from_temperature_array(
    temperature_array: Union[list[float], np.ndarray],
) -> float:
    """
    Get the median temperature from a temperature array using numpy.

    Args:
        temperature_array: Array of temperature values

    Returns:
        Median temperature value
    """
    return float(np.median(temperature_array))


def get_standard_deviation_from_temperature_array(
    temperature_array: Union[list[float], np.ndarray],
) -> float:
    """
    Get the standard deviation from a temperature array using numpy.

    Args:
        temperature_array: Array of temperature values

    Returns:
        Standard deviation of temperatures
    """
    return float(np.std(temperature_array))


def get_variance_from_temperature_array(
    temperature_array: Union[list[float], np.ndarray],
) -> float:
    """
    Get the variance from a temperature array using numpy.

    Args:
        temperature_array: Array of temperature values

    Returns:
        Variance of temperatures
    """
    return float(np.var(temperature_array))


def get_percentile_from_temperature_array(
    temperature_array: Union[list[float], np.ndarray], percentile: float
) -> float:
    """
    Get a specific percentile from a temperature array.

    Args:
        temperature_array: Array of temperature values
        percentile: Percentile to calculate (0-100)

    Returns:
        Temperature value at the specified percentile
    """
    return float(np.percentile(temperature_array, percentile))


def get_mta() -> float:
    """
    Get the MTA (Maximum Allowable Temperature).

    Returns:
        Default MTA value
    """
    # TODO: Implement logic to get MTA based on context/equipment type
    return 100.0


def convert_temperature_unit(
    temperature: float, unit_from: str = "Kelvin", unit_to: str = "Celsius"
) -> float:
    """
    Convert temperature from one unit to another.

    Args:
        temperature: The temperature to convert
        unit_from: The unit to convert from (Celsius, Fahrenheit, Kelvin)
        unit_to: The unit to convert to (Celsius, Fahrenheit, Kelvin)

    Returns:
        The converted temperature

    Raises:
        ValueError: If unsupported temperature unit is provided
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
