"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Temperature calculation utilities for thermal image analysis.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

from typing import Union

import numpy as np  # type: ignore

# ============================================================
# CLASSIFICATION THRESHOLDS (ADJUSTABLE)
# ============================================================

# Delta-T thresholds (in °C)
DELTA_T_CRITICAL = 15.0
DELTA_T_WARNING = 8.0

# Standard Deviation thresholds (in °C)
STD_DEV_CRITICAL = 5.0
STD_DEV_WARNING = 2.5


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
        unit_from: The unit to convert from (Celsius, Fahrenheit, Kelvin, K, C, F, °C, °F)
        unit_to: The unit to convert to (Celsius, Fahrenheit, Kelvin, K, C, F, °C, °F)

    Returns:
        The converted temperature

    Raises:
        ValueError: If unsupported temperature unit is provided
    """
    # Normalize unit names
    unit_from = _normalize_temperature_unit(unit_from)
    unit_to = _normalize_temperature_unit(unit_to)

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


def _normalize_temperature_unit(unit: str) -> str:
    """
    Normalize temperature unit name.

    Args:
        unit: Temperature unit string

    Returns:
        Normalized unit name (Celsius, Fahrenheit, or Kelvin)
    """
    unit_upper = unit.upper().strip()

    if unit_upper in ["C", "°C", "CELSIUS"]:
        return "Celsius"
    elif unit_upper in ["F", "°F", "FAHRENHEIT"]:
        return "Fahrenheit"
    elif unit_upper in ["K", "KELVIN"]:
        return "Kelvin"
    else:
        return unit  # Return original if not recognized


def convert_temperature_value_to_celsius(value: float, original_unit: str) -> float:
    """
    Convert a temperature value to Celsius from any unit.

    Args:
        value: Temperature value
        original_unit: Original temperature unit

    Returns:
        Temperature in Celsius
    """
    if value is None:
        return None  # type: ignore

    return convert_temperature_unit(value, original_unit, "Celsius")


def generate_severity_grade(
    delta_t: float,
    std_dev: float,
    delta_t_critical: float = DELTA_T_CRITICAL,
    delta_t_warning: float = DELTA_T_WARNING,
    std_dev_critical: float = STD_DEV_CRITICAL,
    std_dev_warning: float = STD_DEV_WARNING,
) -> dict:
    """
    Generate severity grade classification based on Delta-T and Standard Deviation.

    Classification levels:
        - Normal (0): Both parameters within acceptable limits
        - Warning (1): At least one parameter exceeds warning threshold
        - Critical (2): At least one parameter exceeds critical threshold

    Args:
        delta_t: Temperature delta (max - min) in Celsius
        std_dev: Standard deviation of temperature array in Celsius
        delta_t_critical: Critical threshold for delta_t (default: 15.0°C)
        delta_t_warning: Warning threshold for delta_t (default: 8.0°C)
        std_dev_critical: Critical threshold for std_dev (default: 5.0°C)
        std_dev_warning: Warning threshold for std_dev (default: 2.5°C)

    Returns:
        Dictionary with classification results:
            - status: "Normal", "Alerta", or "Crítico"
            - criticality: 0 (Normal), 1 (Warning), 2 (Critical)
            - observations: List of observation strings
            - delta_t_status: Status for delta_t parameter
            - std_dev_status: Status for std_dev parameter

    Example:
        >>> result = generate_severity_grade(delta_t=10.5, std_dev=3.2)
        >>> print(result["status"])
        "Alerta"
    """
    observations = []
    delta_t_status = "Normal"
    std_dev_status = "Normal"

    # Evaluate Critical conditions
    is_critical = False
    if delta_t >= delta_t_critical:
        is_critical = True
        delta_t_status = "Crítico"
        observations.append(
            f"Delta-T ({delta_t:.2f}°C) excedeu o limite crítico de {delta_t_critical}°C"
        )

    if std_dev >= std_dev_critical:
        is_critical = True
        std_dev_status = "Crítico"
        observations.append(
            f"Desvio Padrão ({std_dev:.2f}°C) excedeu o limite crítico de {std_dev_critical}°C"
        )

    if is_critical:
        return {
            "status": "Crítico",
            "criticality": 2,
            "observations": observations,
            "delta_t_status": delta_t_status,
            "std_dev_status": std_dev_status,
        }

    # Evaluate Warning conditions
    is_warning = False
    if delta_t >= delta_t_warning:
        is_warning = True
        delta_t_status = "Alerta"
        observations.append(
            f"Delta-T ({delta_t:.2f}°C) excedeu o limite de alerta de {delta_t_warning}°C"
        )

    if std_dev >= std_dev_warning:
        is_warning = True
        std_dev_status = "Alerta"
        observations.append(
            f"Desvio Padrão ({std_dev:.2f}°C) excedeu o limite de alerta de {std_dev_warning}°C"
        )

    if is_warning:
        return {
            "status": "Alerta",
            "criticality": 1,
            "observations": observations,
            "delta_t_status": delta_t_status,
            "std_dev_status": std_dev_status,
        }

    # Normal condition
    return {
        "status": "Normal",
        "criticality": 0,
        "observations": ["Todos os parâmetros dentro dos limites aceitáveis"],
        "delta_t_status": delta_t_status,
        "std_dev_status": std_dev_status,
    }
