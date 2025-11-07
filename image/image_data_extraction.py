"""
Thermal image data extraction module.
Extracts metadata and properties from FLIR thermal images.
"""

import os
import sys

scriptdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"Script directory: {scriptdir}")
os.chdir(scriptdir)
sys.path.append(scriptdir)

import json
import os
from typing import Any, Dict, List, Optional, Union

import clr
import openpyxl
import pandas as pd
from openpyxl.utils.dataframe import dataframe_to_rows

from config.settings import settings
from utils.LoggerConfig import LoggerConfig

logger = LoggerConfig.add_file_logger(
    name="data_extraction", filename=None, dir_name=None, prefix=None
)

# Add the path to the directory containing the compiled DLL
DLL_PATH = os.path.join(settings.BASE_DIR, "ThermalCameraLibrary")

clr.AddReference(os.path.join(DLL_PATH, "ThermalCamera.dll"))
clr.AddReference(os.path.join(DLL_PATH, "Flir.Atlas.Live.dll"))
clr.AddReference(os.path.join(DLL_PATH, "Flir.Atlas.Image.dll"))
clr.AddReference("System")

import Flir.Atlas.Image as Image  # type: ignore

# Import the necessary classes from the assembly
import Flir.Atlas.Live as live  # type: ignore
from System import Byte  # type: ignore


def extract_all_attributes(
    obj: Any, description: str = "", max_depth: int = 3, current_depth: int = 0
) -> Union[Dict[str, Any], str]:
    """
    Recursively extract all attributes from an object.

    Args:
        obj: Object to extract attributes from
        description: Description for logging purposes
        max_depth: Maximum recursion depth
        current_depth: Current recursion depth

    Returns:
        Dictionary of extracted attributes or string representation
    """
    if current_depth >= max_depth:
        return str(obj)

    result = {}

    try:
        for attr in dir(obj):
            if not attr.startswith("_") and not callable(getattr(obj, attr)):
                try:
                    value = getattr(obj, attr)
                    if value is not None:
                        result[attr] = _process_attribute_value(
                            value, attr, description, max_depth, current_depth
                        )
                except Exception as e:
                    logger.warning(f"Could not extract {attr} from {description}: {e}")
                    continue
    except Exception as e:
        logger.warning(f"Could not iterate attributes of {description}: {e}")
        return str(obj)

    return result


def _process_attribute_value(
    value: Any, attr: str, description: str, max_depth: int, current_depth: int
) -> Any:
    """Process individual attribute values for serialization."""
    # Handle different types of values
    if hasattr(value, "tolist"):
        return value.tolist()
    elif isinstance(value, (str, int, float, bool)):
        return value
    elif isinstance(value, (list, tuple)):
        return list(value)
    elif isinstance(value, dict):
        return _clean_dict(value)
    elif hasattr(value, "__dict__"):
        # Recursively extract nested objects
        return extract_all_attributes(
            value,
            f"{description}.{attr}",
            max_depth,
            current_depth + 1,
        )
    else:
        return _serialize_value(value)


def _clean_dict(value_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Clean dictionary with potential non-serializable values."""
    clean_dict = {}
    for k, v in value_dict.items():
        try:
            json.dumps(v)
            clean_dict[k] = v
        except (TypeError, ValueError):
            clean_dict[k] = _serialize_value(v)
    return clean_dict


def _serialize_value(value: Any) -> Union[float, str, list]:
    """Convert non-serializable values to serializable format."""
    try:
        json.dumps(value)  # Test if JSON serializable
        return value
    except (TypeError, ValueError):
        # Handle lists first
        if isinstance(value, (list, tuple)):
            return [_serialize_value(item) for item in value]
        # Handle non-serializable types (like IFDRational)
        elif hasattr(value, "__float__"):
            try:
                value_parsed = float(value)
                if value_parsed.is_integer():
                    return int(value_parsed)  # Return as int if no decimal part
                else:
                    return value_parsed
            except Exception:
                return str(value)
        else:
            # Try to handle complex .NET types
            net_result = _handle_dotnet_types(value)
            if net_result is not None:
                return net_result
            return str(value)


def _handle_dotnet_types(value: Any) -> Optional[Dict[str, Any]]:
    """
    Handle complex .NET types and convert them to serializable dictionaries.

    Args:
        value: The .NET object to convert

    Returns:
        Dictionary representation of the .NET object or None if not handled
    """
    try:
        # Handle .NET Color objects
        if (
            "Color" in str(type(value))
            and hasattr(value, "A")
            and hasattr(value, "R")
            and hasattr(value, "G")
            and hasattr(value, "B")
        ):
            return {
                "A": int(value.A) if hasattr(value, "A") else 255,
                "R": int(value.R) if hasattr(value, "R") else 0,
                "G": int(value.G) if hasattr(value, "G") else 0,
                "B": int(value.B) if hasattr(value, "B") else 0,
                "Name": getattr(value, "Name", None),
                "IsKnownColor": getattr(value, "IsKnownColor", False),
            }

        # Handle .NET Rectangle/Area objects
        elif (
            hasattr(value, "X")
            and hasattr(value, "Y")
            and hasattr(value, "Width")
            and hasattr(value, "Height")
        ):
            return {
                "X": int(value.X) if hasattr(value, "X") else 0,
                "Y": int(value.Y) if hasattr(value, "Y") else 0,
                "Width": int(value.Width) if hasattr(value, "Width") else 0,
                "Height": int(value.Height) if hasattr(value, "Height") else 0,
            }

        # Handle .NET Point objects
        elif (
            hasattr(value, "X") and hasattr(value, "Y") and not hasattr(value, "Width")
        ):
            return {
                "X": int(value.X) if hasattr(value, "X") else 0,
                "Y": int(value.Y) if hasattr(value, "Y") else 0,
            }

        # Handle Range objects (with Min/Max or similar properties)
        elif hasattr(value, "Minimum") and hasattr(value, "Maximum"):
            return {
                "Minimum": float(value.Minimum) if hasattr(value, "Minimum") else None,
                "Maximum": float(value.Maximum) if hasattr(value, "Maximum") else None,
            }
        elif hasattr(value, "Min") and hasattr(value, "Max"):
            return {
                "Min": float(value.Min) if hasattr(value, "Min") else None,
                "Max": float(value.Max) if hasattr(value, "Max") else None,
            }

        # Handle thermal range strings like "[-0,0959524585098706 - 29,6382336093277]"
        elif (
            isinstance(str(value), str)
            and "[" in str(value)
            and "-" in str(value)
            and "]" in str(value)
        ):
            range_str = str(value).strip("[]")
            if " - " in range_str:
                try:
                    parts = range_str.split(" - ")
                    if len(parts) == 2:
                        min_val = float(parts[0].replace(",", "."))
                        max_val = float(parts[1].replace(",", "."))
                        return {
                            "Min": min_val,
                            "Max": max_val,
                            "OriginalString": str(value),
                        }
                except Exception:
                    pass

        # Return None if no specific handler found
        return None

    except Exception as e:
        logger.warning(f"Error handling .NET type {type(value)}: {e}")
        return None


def safe_extract_attribute(
    obj: Any,
    attribute_name: str,
    default: Any = None,
    multi_level_attr: str = None,
    method_params: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Safely extract an attribute from the thermal image or execute a method if needed.

    Args:
        obj: Object to extract attribute from
        attribute_name: Name of the attribute to extract or method to call
        default: Default value to return if attribute is not found
        method_params: Dictionary of parameters to pass to method if it's callable
        multi_level_attr: If provided, extract this attribute from the result of the method call

    Returns:
        Extracted attribute value or method result, or default
    Tests:
        obj=thermal_image
        attribute_name="Statistics"
        default=None
        method_params={"Min":"Value"}
        multi_level_attr="Value"
    """
    try:
        attr = getattr(obj, attribute_name, None)

        if attr is None:
            logger.warning(f"Attribute/method {attribute_name} not found")
            return default

        # Check if it's a callable method
        if callable(attr):
            try:
                if method_params:
                    # Pass parameters if provided
                    value = attr(**method_params)
                else:
                    # Call method without parameters
                    value = attr()
            except Exception as e:
                logger.warning(f"Error calling method {attribute_name}: {e}")
                return default
        else:
            if not multi_level_attr:
                # It's a regular attribute
                value = attr
            else:
                value = getattr(attr, multi_level_attr, None)

        # Serialize the value
        rasterized_value = _serialize_value(value)
        if rasterized_value is not None:
            return rasterized_value
        else:
            logger.warning(
                f"Attribute/method {attribute_name} returned None or not serializable"
            )
            return default

    except Exception as e:
        logger.warning(f"Error extracting {attribute_name}: {e}")
        return default


def extract_image_metadata(thermal_image: Any) -> Dict[str, Any]:
    """
    Extract basic image metadata safely.

    Args:
        thermal_image: Thermal image object

    Returns:
        Image metadata dictionary
    """
    TemperatureUnitEnum = {0: "Celsius", 1: "Fahrenheit", 2: "Kelvin", 3: "Signal"}
    DistanceUnitEnum = {0: "Meter", 1: "Feet"}
    ColorDistributionEnum = {
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

    TemperatureUnit = safe_extract_attribute(thermal_image, "TemperatureUnit")
    DistanceUnit = safe_extract_attribute(thermal_image, "DistanceUnit")
    ColorDistribution = safe_extract_attribute(thermal_image, "ColorDistribution")

    metadata_dict = {
        "FileName": safe_extract_attribute(thermal_image, "Title"),
        "Height": safe_extract_attribute(thermal_image, "Height"),
        "Width": safe_extract_attribute(thermal_image, "Width"),
        "FrameCount": safe_extract_attribute(thermal_image, "Count"),
        "TemperatureUnit": TemperatureUnitEnum.get(TemperatureUnit, TemperatureUnit),
        "DistanceUnit": DistanceUnitEnum.get(DistanceUnit, DistanceUnit),
        "ColorDistribution": ColorDistributionEnum.get(
            ColorDistribution, ColorDistribution
        ),
        "Description": safe_extract_attribute(thermal_image, "Description"),
        "DateTime": safe_extract_attribute(thermal_image, "DateTime"),
        "DateTaken": safe_extract_attribute(thermal_image, "DateTaken"),
        "ContainsUltraMaxData": safe_extract_attribute(
            thermal_image, "ContainsUltraMaxData"
        ),
        "MaxSignalValue": safe_extract_attribute(thermal_image, "MaxSignalValue"),
        "MinSignalValue": safe_extract_attribute(thermal_image, "MinSignalValue"),
        "OverflowSignalValue": safe_extract_attribute(
            thermal_image, "OverflowSignalValue"
        ),
        "Precision": safe_extract_attribute(thermal_image, "Precision"),
    }

    return metadata_dict


def extract_gps_information(thermal_image: Any) -> Optional[Dict[str, Any]]:
    """
    Safely extract GPS information from thermal image.

    Args:
        thermal_image: Thermal image object

    Returns:
        GPS information dictionary or None if not available
    """
    if thermal_image.GpsInformation is None:
        return None

    try:
        gps_info = thermal_image.GpsInformation
        return {
            "IsValid": safe_extract_attribute(gps_info, "IsValid"),
            "Altitude": safe_extract_attribute(gps_info, "Altitude"),
            "AltitudeRef": safe_extract_attribute(gps_info, "AltitudeRef"),
            "Dop": safe_extract_attribute(gps_info, "Dop"),
            "Latitude": safe_extract_attribute(gps_info, "Latitude"),
            "LatitudeRef": safe_extract_attribute(gps_info, "LatitudeRef"),
            "Longitude": safe_extract_attribute(gps_info, "Longitude"),
            "LongitudeRef": safe_extract_attribute(gps_info, "LongitudeRef"),
            "MapDatum": safe_extract_attribute(gps_info, "MapDatum"),
            "Satellites": safe_extract_attribute(gps_info, "Satellites"),
            "Timestamp": safe_extract_attribute(gps_info, "Timestamp"),
        }
    except Exception as e:
        logger.warning(f"Error extracting GPS information: {e}")
        return None


def extract_camera_information(thermal_image: Any) -> Optional[Dict[str, Any]]:
    """
    Safely extract camera information from thermal image.

    Args:
        thermal_image: Thermal image object

    Returns:
        Camera information dictionary or None if not available
    """
    if thermal_image.CameraInformation is None:
        return None

    try:
        camera_info_obj = thermal_image.CameraInformation
        camera_info = {
            "Model": safe_extract_attribute(camera_info_obj, "Model"),
            "SerialNumber": safe_extract_attribute(camera_info_obj, "SerialNumber"),
            "Lens": safe_extract_attribute(camera_info_obj, "Lens"),
            "Filter": safe_extract_attribute(camera_info_obj, "Filter"),
            "Fov": safe_extract_attribute(camera_info_obj, "Fov"),
        }

        # Safely extract range information
        if hasattr(camera_info_obj, "Range") and camera_info_obj.Range is not None:
            range_obj = camera_info_obj.Range
            camera_info["Range"] = {
                "Maximum": safe_extract_attribute(range_obj, "Maximum"),
                "Minimum": safe_extract_attribute(range_obj, "Minimum"),
            }

        return camera_info
    except Exception as e:
        logger.warning(f"Error extracting camera information: {e}")
        return None


def extract_gas_quantification_result(thermal_image: Any) -> Optional[Dict[str, Any]]:
    """
    Safely extract gas quantification result from thermal image.

    Args:
        thermal_image: Thermal image object

    Returns:
        Gas quantification result dictionary or None if not available
    """
    if thermal_image.GasQuantificationResult is None:
        return None

    try:
        gas_result = thermal_image.GasQuantificationResult
        return {
            "Flow": safe_extract_attribute(gas_result, "Flow"),
            "Concentration": safe_extract_attribute(gas_result, "Concentration"),
        }
    except Exception as e:
        logger.warning(f"Error extracting gas quantification result: {e}")
        return None


def extract_gas_quantification_input(thermal_image: Any) -> Optional[Dict[str, Any]]:
    """
    Safely extract gas quantification input from thermal image.

    Args:
        thermal_image: Thermal image object

    Returns:
        Gas quantification input dictionary or None if not available
    """
    if thermal_image.GasQuantificationInput is None:
        return None

    try:
        gas_input = thermal_image.GasQuantificationInput
        return {
            "IsValid": safe_extract_attribute(gas_input, "IsValid"),
            "AmbientTemperature": safe_extract_attribute(
                gas_input, "AmbientTemperature"
            ),
            "Gas": safe_extract_attribute(gas_input, "Gas"),
            "LeakType": safe_extract_attribute(gas_input, "LeakType"),
            "WindSpeed": safe_extract_attribute(gas_input, "WindSpeed"),
            "Distance": safe_extract_attribute(gas_input, "Distance"),
            "ThresholdDeltaTemperature": safe_extract_attribute(
                gas_input, "ThresholdDeltaTemperature"
            ),
            "Emissive": safe_extract_attribute(gas_input, "Emissive"),
        }
    except Exception as e:
        logger.warning(f"Error extracting gas quantification input: {e}")
        return None


def extract_compass_information(thermal_image: Any) -> Optional[Dict[str, Any]]:
    """
    Safely extract compass information from thermal image.

    Args:
        thermal_image: Thermal image object

    Returns:
        Compass information dictionary or None if not available
    """
    if thermal_image.CompassInformation is None:
        return None

    try:
        compass_info = thermal_image.CompassInformation
        return {
            "Degrees": safe_extract_attribute(compass_info, "Degrees"),
            "Roll": safe_extract_attribute(compass_info, "Roll"),
            "Pitch": safe_extract_attribute(compass_info, "Pitch"),
        }
    except Exception as e:
        logger.warning(f"Error extracting compass information: {e}")
        return None


def extract_thermal_parameters(thermal_image: Any) -> Optional[Dict[str, Any]]:
    """
    Safely extract thermal parameters from thermal image.

    Args:
        thermal_image: Thermal image object

    Returns:
        Thermal parameters dictionary or None if not available
    """
    if thermal_image.ThermalParameters is None:
        return None

    try:
        thermal_params = thermal_image.ThermalParameters
        return {
            "AtmosphericTemperature": safe_extract_attribute(
                thermal_params, "AtmosphericTemperature"
            ),
            "Distance": safe_extract_attribute(thermal_params, "Distance"),
            "Emissivity": safe_extract_attribute(thermal_params, "Emissivity"),
            "ExternalOpticsTemperature": safe_extract_attribute(
                thermal_params, "ExternalOpticsTemperature"
            ),
            "ExternalOpticsTransmission": safe_extract_attribute(
                thermal_params, "ExternalOpticsTransmission"
            ),
            "ReferenceTemperature": safe_extract_attribute(
                thermal_params, "ReferenceTemperature"
            ),
            "ReflectedTemperature": safe_extract_attribute(
                thermal_params, "ReflectedTemperature"
            ),
            "RelativeHumidity": safe_extract_attribute(
                thermal_params, "RelativeHumidity"
            ),
            "Transmission": safe_extract_attribute(thermal_params, "Transmission"),
        }
    except Exception as e:
        logger.warning(f"Error extracting thermal parameters: {e}")
        return None


def extract_zoom_information(thermal_image: Any) -> Optional[Dict[str, Any]]:
    """
    Safely extract zoom information from thermal image.

    Args:
        thermal_image: Thermal image object

    Returns:
        Zoom information dictionary or None if not available
    """
    if thermal_image.Zoom is None:
        return None

    try:
        zoom_info = thermal_image.Zoom
        return {
            "Factor": safe_extract_attribute(zoom_info, "Factor"),
            "PanX": safe_extract_attribute(zoom_info, "PanX"),
            "PanY": safe_extract_attribute(zoom_info, "PanY"),
        }
    except Exception as e:
        logger.warning(f"Error extracting zoom information: {e}")
        return None


def extract_statistics_information(thermal_image: Any) -> Optional[Dict[str, Any]]:
    """
    Safely extract statistics information from thermal image.

    Args:
        thermal_image: Thermal image object

    Returns:
        Statistics information dictionary or None if not available
    """
    if thermal_image.Statistics is None:
        return None

    try:
        stats_info = thermal_image.Statistics
        statistics_data = {
            "Min": safe_extract_attribute(stats_info, "Min", multi_level_attr="Value"),
            "Max": safe_extract_attribute(stats_info, "Max", multi_level_attr="Value"),
            "Average": safe_extract_attribute(
                stats_info, "Average", multi_level_attr="Value"
            ),
            "StandardDeviation": safe_extract_attribute(
                stats_info, "StandardDeviation", multi_level_attr="Value"
            ),
        }

        # Extract HotSpot coordinates
        if hasattr(stats_info, "HotSpot") and stats_info.HotSpot is not None:
            hot_spot = stats_info.HotSpot
            statistics_data["HotSpot"] = {
                "X": safe_extract_attribute(hot_spot, "X"),
                "Y": safe_extract_attribute(hot_spot, "Y"),
            }
        else:
            statistics_data["HotSpot"] = None

        # Extract ColdSpot coordinates
        if hasattr(stats_info, "ColdSpot") and stats_info.ColdSpot is not None:
            cold_spot = stats_info.ColdSpot
            statistics_data["ColdSpot"] = {
                "X": safe_extract_attribute(cold_spot, "X"),
                "Y": safe_extract_attribute(cold_spot, "Y"),
            }
        else:
            statistics_data["ColdSpot"] = None

        return statistics_data
    except Exception as e:
        logger.warning(f"Error extracting statistics information: {e}")
        return None


def extract_measurements(collection: Any) -> List[Any]:
    """
    Extract measurements from a collection.

    Args:
        collection: Collection of measurements

    Returns:
        List of measurement dictionaries
    """
    generic_types = [
        "MeasurementEllipses",
        "MeasurementRectangles",
        "MeasurementPolygons",
        "MeasurementLines",
        "MeasurementDeltas",
        "MeasurementSpots",
    ]
    measurements = []

    for measurement_type in generic_types:
        if not hasattr(collection, measurement_type):
            continue
        collection_measurement = getattr(collection, measurement_type, None)
        for i in range(collection_measurement.Count):
            measurement = collection[i]
            measurements.append(
                {
                    "index": i,
                    "Type": measurement_type,
                    "Value": safe_extract_attribute(
                        measurement, "Value", multi_level_attr="Value"
                    ),
                    "X": measurement.X,
                    "Y": measurement.Y,
                }
            )

    return measurements


def extract_generic_collection(
    thermal_image: Any, collection_name: str
) -> Optional[List[Any]]:
    """
    Safely extract a generic collection from thermal image.

    Args:
        thermal_image: Thermal image object
        collection_name: Name of the collection to extract

    Returns:
        Collection data dictionary or None if not available
    Tests:
        collection_name = "Sensors"
        collection_name = "Alarms"
        collection_name = "Isotherms"
        collection_name = "Histogram"
        collection_name = "Measurements"
    """

    """
    TODO:
        [ ] - "Sensors"
        [ ] - "Alarms"
        [ ] - "Isotherms" 
        [ ] - "Histogram" 
        [x] - "Measurements"
    """
    collection = getattr(thermal_image, collection_name, None)

    if collection is None:
        return []

    collection_size = collection.Count
    if collection_size == 0:
        logger.warning(f"{collection_name} collection is empty")
        return []

    if collection_name == "Measurements":
        try:
            measurements = extract_measurements(collection)
            return measurements
        except Exception as e:
            logger.warning(f"Error extracting measurements from {collection_name}: {e}")
            return []

    try:
        attributes = extract_all_attributes(collection, f"{collection_name}")
        return attributes
    except Exception as e:
        logger.warning(f"Error extracting {collection_name}: {e}")
        return []


def extract_trigger_data(thermal_image: Any) -> Optional[Dict[str, Any]]:
    """
    Safely extract trigger data from thermal image.

    Args:
        thermal_image: Thermal image object

    Returns:
        Trigger data dictionary or None if not available
    """
    if not hasattr(thermal_image, "Trigger") or thermal_image.Trigger is None:
        logger.warning("TriggerData not found in thermal image")
        return None

    try:
        trigger_data = thermal_image.Trigger
        return {
            "IsValid": safe_extract_attribute(trigger_data, "IsValid"),
            "Counter": safe_extract_attribute(trigger_data, "Counter"),
            "IsTriggered": safe_extract_attribute(trigger_data, "IsTriggered"),
            "Flags": safe_extract_attribute(trigger_data, "Flags"),
        }
    except Exception as e:
        logger.warning(f"Error extracting trigger data: {e}")
        return None


def extract_palette(thermal_image: Any) -> Optional[Dict[str, Any]]:
    """
    Safely extract palette information from thermal image.

    Args:
        thermal_image: Thermal image object

    Returns:
        Palette information dictionary or None if not available
    """
    if not hasattr(thermal_image, "Palette") or thermal_image.Palette is None:
        logger.warning("Palette not found in thermal image")
        return None

    try:
        palette = thermal_image.Palette
        return {
            "Name": safe_extract_attribute(palette, "Name"),
            "IsInverted": safe_extract_attribute(palette, "IsInverted"),
            "Version": safe_extract_attribute(palette, "Version"),
            "OverflowColor": safe_extract_attribute(palette, "OverflowColor"),
            "UnderflowColor": safe_extract_attribute(palette, "UnderflowColor"),
            "AboveSpanColor": safe_extract_attribute(palette, "AboveSpanColor"),
            "BelowSpanColor": safe_extract_attribute(palette, "BelowSpanColor"),
            "PaletteColors": extract_generic_collection(palette, "PaletteColors"),
        }

        # TODO: collect palette colors
        # PaletteColors = palette.PaletteColors

        # TODO: collect palette manager
        # palleteManager = thermal_image.PaletteManager
    except Exception as e:
        logger.warning(f"Error extracting palette information: {e}")
        return None


def extract_fusion_information(thermal_image: Any) -> Optional[Dict[str, Any]]:
    """
    Safely extract fusion information from thermal image.

    Args:
        thermal_image: Thermal image object

    Returns:
        Fusion information dictionary or None if not available
    """
    if not hasattr(thermal_image, "Fusion") or thermal_image.Fusion is None:
        logger.warning("Fusion not found in thermal image")
        return None

    try:
        fusion = thermal_image.Fusion
        fusion_data = {
            "Mode": safe_extract_attribute(fusion, "Mode"),
            "PanX": safe_extract_attribute(fusion, "PanX"),
            "PanY": safe_extract_attribute(fusion, "PanY"),
            "Rotation": safe_extract_attribute(fusion, "Rotation"),
        }

        # Extract fusion mode settings
        if hasattr(fusion, "VisualOnly") and fusion.VisualOnly is not None:
            fusion_data["VisualOnly"] = extract_all_attributes(
                fusion.VisualOnly, "VisualOnly"
            )
        else:
            fusion_data["VisualOnly"] = None

        if hasattr(fusion, "ThermalOnly") and fusion.ThermalOnly is not None:
            fusion_data["ThermalOnly"] = extract_all_attributes(
                fusion.ThermalOnly, "ThermalOnly"
            )
        else:
            fusion_data["ThermalOnly"] = None

        if hasattr(fusion, "Msx") and fusion.Msx is not None:
            fusion_data["Msx"] = extract_all_attributes(fusion.Msx, "Msx")
        else:
            fusion_data["Msx"] = None

        if hasattr(fusion, "PictureInPicture") and fusion.PictureInPicture is not None:
            fusion_data["PictureInPicture"] = extract_all_attributes(
                fusion.PictureInPicture, "PictureInPicture"
            )
        else:
            fusion_data["PictureInPicture"] = None

        if hasattr(fusion, "Blending") and fusion.Blending is not None:
            fusion_data["Blending"] = extract_all_attributes(
                fusion.Blending, "Blending"
            )
        else:
            fusion_data["Blending"] = None

        # Extract thermal fusion settings
        if (
            hasattr(fusion, "ThermalFusionAbove")
            and fusion.ThermalFusionAbove is not None
        ):
            fusion_data["ThermalFusionAbove"] = extract_all_attributes(
                fusion.ThermalFusionAbove, "ThermalFusionAbove"
            )
        else:
            fusion_data["ThermalFusionAbove"] = None

        if (
            hasattr(fusion, "ThermalFusionBelow")
            and fusion.ThermalFusionBelow is not None
        ):
            fusion_data["ThermalFusionBelow"] = extract_all_attributes(
                fusion.ThermalFusionBelow, "ThermalFusionBelow"
            )
        else:
            fusion_data["ThermalFusionBelow"] = None

        if (
            hasattr(fusion, "ThermalFusionInterval")
            and fusion.ThermalFusionInterval is not None
        ):
            fusion_data["ThermalFusionInterval"] = extract_all_attributes(
                fusion.ThermalFusionInterval, "ThermalFusionInterval"
            )
        else:
            fusion_data["ThermalFusionInterval"] = None

        # Note: VisualImage is excluded as it's a Bitmap that should be disposed after use
        # and would be too large for JSON serialization

        return fusion_data
    except Exception as e:
        logger.warning(f"Error extracting fusion information: {e}")
        return None


def get_image_array(thermal_image: Any) -> Optional[List[List[List[int]]]]:
    """
    Safely extract the image array from the thermal image.

    The ImageArray() returns a byte[,,] representing RGB data (3x8 bit).

    Args:
        thermal_image: Thermal image object

    Returns:
        Image array as a 3D list [height][width][rgb] or None if not available
    """
    try:
        # Get the 3D byte array (height, width, 3 for RGB)
        image_array = thermal_image.ImageArray()

        if image_array is None:
            logger.warning("ImageArray returned None")
            return None

        # Get dimensions
        height = image_array.GetLength(0)  # First dimension
        width = image_array.GetLength(1)  # Second dimension
        channels = image_array.GetLength(2)  # Third dimension (should be 3 for RGB)

        logger.info(f"Image array dimensions: {height}x{width}x{channels}")

        # Convert 3D byte array to Python list
        result = []
        for h in range(height):
            row = []
            for w in range(width):
                pixel = []
                for c in range(channels):
                    # Convert byte to int (0-255)
                    pixel.append(int(image_array[h, w, c]))
                row.append(pixel)
            result.append(row)

        return result

    except Exception as e:
        logger.warning(f"Error extracting image array: {e}")
        return None


def extract_image_dataframe(
    image_array: List[List[List[int]]],
    one_based_index: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Convert 3D image array to pandas DataFrames.

    Args:
        image_array: 3D list representing image data [height][width][rgb]

    Returns:
        Tuple of (flattened_df, pivoted_df):
        - flattened_df: DataFrame with columns Y, X, R, G, B representing pixel data (1-based indexing)
        - pivoted_df: DataFrame with Y as rows, X as columns, and "r,g,b" or "r,g,b,a" as cell values (1-based indexing)
    """
    if image_array is None:
        logger.warning("Image array is None, returning empty DataFrames")
        return pd.DataFrame(), pd.DataFrame()

    try:
        # Determine number of channels from the first pixel
        num_channels = (
            len(image_array[0][0])
            if len(image_array) > 0 and len(image_array[0]) > 0
            else 0
        )

        # Flatten the 3D array (height, width, channels) to 2D for DataFrame
        # Each row represents a pixel with columns for Y, X, R, G, B, (A if available)
        # Using 1-based indexing for consistency with image dimensions
        flattened_data = []
        pivoted_data = {}

        for h in range(len(image_array)):
            for w in range(len(image_array[h])):
                pixel = image_array[h][w]
                r = pixel[0] if len(pixel) > 0 else 0
                g = pixel[1] if len(pixel) > 1 else 0
                b = pixel[2] if len(pixel) > 2 else 0

                # Flattened data - using 1-based indexing
                pixel_data = {
                    "Y": h + 1 if one_based_index else h,
                    "X": w + 1 if one_based_index else w,
                    "R": r,
                    "G": g,
                    "B": b,
                }

                # Add alpha channel only if it exists
                if len(pixel) > 3:
                    a = pixel[3]
                    pixel_data["A"] = a
                    rgb_string = f"{r},{g},{b},{a}"
                else:
                    rgb_string = f"{r},{g},{b}"

                flattened_data.append(pixel_data)

                # Pivoted data preparation
                y_index = h + 1 if one_based_index else h
                x_index = w + 1 if one_based_index else w
                if y_index not in pivoted_data:
                    pivoted_data[y_index] = {}
                pivoted_data[y_index][x_index] = rgb_string

        # Create flattened DataFrame
        flattened_df = pd.DataFrame(flattened_data)
        logger.info(
            f"Created flattened DataFrame with shape: {flattened_df.shape} and {num_channels} channels"
        )

        # Create pivoted DataFrame
        if pivoted_data:
            pivoted_df = pd.DataFrame(pivoted_data).T  # Transpose to have Y as rows
            pivoted_df.index.name = "Y"
            pivoted_df.columns.name = "X"
            logger.info(f"Created pivoted DataFrame with shape: {pivoted_df.shape}")
        else:
            pivoted_df = pd.DataFrame()

        return flattened_df, pivoted_df

    except Exception as e:
        logger.error(f"Error creating DataFrames from image array: {e}")
        return pd.DataFrame(), pd.DataFrame()


def extract_thermal_image_data(thermal_image: Any) -> Dict[str, Any]:
    """
    Extract all thermal image data safely.

    Args:
        thermal_image: Thermal image object

    Returns:
        Dictionary containing all extracted data
    """
    try:

        thermal_image_dict = {
            "ImageMetaData": extract_image_metadata(thermal_image),
            "GPSInfo": extract_gps_information(thermal_image),
            "CompassInfo": extract_compass_information(thermal_image),
            "Camera": extract_camera_information(thermal_image),
            "ThermalParameters": extract_thermal_parameters(thermal_image),
            "GasQuantificationResult": extract_gas_quantification_result(thermal_image),
            "GasQuantificationInput": extract_gas_quantification_input(thermal_image),
            "Zoom": extract_zoom_information(thermal_image),
            "Statistics": extract_statistics_information(thermal_image),
            "Sensors": extract_generic_collection(
                thermal_image, collection_name="Sensors"
            ),
            "Alarms": extract_generic_collection(
                thermal_image, collection_name="Alarms"
            ),
            "Isotherms": extract_generic_collection(
                thermal_image, collection_name="Isotherms"
            ),
            "Measurements": extract_generic_collection(
                thermal_image, collection_name="Measurements"
            ),
            "Histogram": extract_generic_collection(
                thermal_image, collection_name="Histogram"
            ),
            "TriggerData": extract_trigger_data(thermal_image),
            "Palette": extract_palette(thermal_image),
            "Fusion": extract_fusion_information(thermal_image),
            "Pipeline": None,
            "Scale": None,
            "ImageArray": get_image_array(thermal_image),
        }
        """
        TODO:
        [ ] - "Sensors"
        [ ] - "Alarms"
        [ ] - "Isotherms" 
        [ ] - "Histogram" 
        [x] - "Measurements"

        [ ] - SensorsCollection
        [ ] - Pipeline
        [ ] - Scale
        [ ] - Histogram
        """
        # SensorsCollection = thermal_image.SensorsCollection
        return thermal_image_dict

    except Exception as e:
        logger.error(f"Error extracting information: {e}")
        raise


def save_extracted_data(data: Dict[str, Any], output_path: str) -> None:
    """
    Save extracted data to JSON file.

    Args:
        data: Data to save
        output_path: Output file path
    """
    try:
        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=2, ensure_ascii=False)
        logger.info(f"Thermogram data saved to: {output_path}")
    except Exception as e:
        logger.error(f"Error saving JSON file: {e}")
        raise


def flatten_dict(
    d: Dict[str, Any], parent_key: str = "", sep: str = "."
) -> Dict[str, Any]:
    """
    Flatten a nested dictionary.

    Args:
        d: Dictionary to flatten
        parent_key: Parent key for nested items
        sep: Separator for nested keys

    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
            # Handle list of dictionaries
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
                else:
                    items.append((f"{new_key}[{i}]", item))
        else:
            items.append((new_key, v))
    return dict(items)


def save_to_excel(
    thermal_image_dict: Dict[str, Any],
    flattened_df: pd.DataFrame,
    pivoted_df: pd.DataFrame,
    output_path: str,
) -> None:
    """
    Save thermal image data and DataFrames to Excel with multiple sheets.

    Args:
        thermal_image_dict: Dictionary containing all thermal image data
        flattened_df: Flattened DataFrame with pixel data
        pivoted_df: Pivoted DataFrame with image grid
        output_path: Output Excel file path
    """
    """
    TODO: limit size for excel:
    1080p (1920×1080): 2,073,600 linhas ❌ NÃO CABE
    720p (1280×720): 921,600 linhas ✅ CABE
    VGA (640×480): 307,200 linhas ✅ CABE
    Térmicas FLIR típicas (640×480): 307,200 linhas ✅ CABE
    """
    try:
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            # Save DataFrames first
            if not flattened_df.empty:
                flattened_df.to_excel(
                    writer, sheet_name="ImageData_Flattened", index=False
                )
                logger.info("Saved flattened image data to Excel")

            if not pivoted_df.empty:
                pivoted_df.to_excel(writer, sheet_name="ImageData_Pivoted", index=True)
                logger.info("Saved pivoted image data to Excel")

            # Process each top-level dictionary
            for key, value in thermal_image_dict.items():
                if key == "ImageArray":
                    # Skip ImageArray as it's already processed in DataFrames
                    continue

                if value is None:
                    # Create sheet with just a note for None values
                    empty_df = pd.DataFrame({"Note": ["No data available"]})
                    empty_df.to_excel(writer, sheet_name=key, index=False)
                    continue

                if isinstance(value, dict):
                    # Flatten nested dictionaries
                    flattened_data = flatten_dict(value)
                    # Convert to DataFrame with Key-Value pairs
                    df = pd.DataFrame(
                        list(flattened_data.items()), columns=["Property", "Value"]
                    )
                    df.to_excel(writer, sheet_name=key, index=False)
                    logger.info(f"Saved {key} data to Excel sheet")

                elif isinstance(value, list):
                    if len(value) == 0:
                        # Empty list
                        empty_df = pd.DataFrame({"Note": ["Empty collection"]})
                        empty_df.to_excel(writer, sheet_name=key, index=False)
                    elif isinstance(value[0], dict):
                        # List of dictionaries - flatten each and create rows
                        flattened_items = []
                        if key == "Measurements":
                            for i, item in enumerate(value):
                                flattened_item = flatten_dict(item)
                                flattened_items.append(flattened_item)
                        else:
                            for i, item in enumerate(value):
                                flattened_item = flatten_dict(item, f"Item{i+1}")
                                flattened_items.append(flattened_item)

                        if flattened_items:
                            # Combine all keys and create DataFrame
                            all_keys = set()
                            for item in flattened_items:
                                all_keys.update(item.keys())

                            rows = []
                            for item in flattened_items:
                                row = {k: item.get(k, None) for k in sorted(all_keys)}
                                rows.append(row)

                            df = pd.DataFrame(rows)
                            df.to_excel(writer, sheet_name=key, index=False)
                        else:
                            empty_df = pd.DataFrame(
                                {"Note": ["No valid data in collection"]}
                            )
                            empty_df.to_excel(writer, sheet_name=key, index=False)
                    else:
                        # List of simple values
                        df = pd.DataFrame(value, columns=[key])
                        df.to_excel(writer, sheet_name=key, index=False)

                    logger.info(f"Saved {key} collection to Excel sheet")

                else:
                    # Simple value
                    df = pd.DataFrame({"Property": [key], "Value": [value]})
                    df.to_excel(writer, sheet_name=key, index=False)
                    logger.info(f"Saved {key} simple value to Excel sheet")

        logger.info(
            f"Successfully saved all thermal image data to Excel: {output_path}"
        )

    except Exception as e:
        logger.error(f"Error saving to Excel: {e}")
        raise


def main() -> None:
    """Main function to execute thermal image data extraction."""
    # file_path = r"C:\projects\tenesso\image_subtraction"
    # img_name = "FLIR1511.jpg"  # Example image name
    # img_name = "IR_26-05-2023_0006.jpg"  # Example image name
    # img_name = "FLIR0089.jpg"
    # img_name = "FLIR0139.jpg"
    file_path = r"C:\projects\tenesso\mvp\runner\static_media\snapshots"
    # img_name = "snapshots_639164718_20250803-172110.jpg"
    # img_name = "snapshots_639164718_20250803-172401.jpg"
    # img_name = "snapshots_639164718_20250803-172522.jpg"
    img_name = "snapshots_639164718_20250811-200602.jpg"

    # Extract base filename for output files
    base_name = os.path.splitext(img_name)[0]
    image_path = os.path.join(file_path, img_name)
    json_filename = os.path.join(file_path, f"{base_name}.json")
    excel_filename = os.path.join(file_path, f"{base_name}_complete.xlsx")

    try:
        # Extract thermal image data
        logger.info(f"Processing thermal image: {image_path}")
        thermal_image = Image.ThermalImageFile(image_path)
        thermal_image_dict = extract_thermal_image_data(thermal_image)

        # Convert 3D image array to DataFrames if available
        flattened_df, pivoted_df = extract_image_dataframe(
            thermal_image_dict["ImageArray"], one_based_index=True
        )

        # Save all data to Excel
        save_to_excel(thermal_image_dict, flattened_df, pivoted_df, excel_filename)

        # Save extracted data to JSON
        save_extracted_data(thermal_image_dict, json_filename)

        # Optional: Extract all attributes for debugging/analysis
        check_data = extract_all_attributes(thermal_image, "thermogram")
        logger.info("Attribute extraction completed successfully")

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise


if __name__ == "__main__":
    main()
