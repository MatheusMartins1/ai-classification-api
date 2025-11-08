import json
import os
from typing import Any, Dict, Optional, Union

from utils.LoggerConfig import LoggerConfig

logger = LoggerConfig.add_file_logger(
    name="object_handler", filename=None, dir_name=None, prefix=None, level_name="ERROR"
)


def serialize_object(
    obj, exclude_methods=True, to_json=False, to_string=True, force_string=True
):
    """
    Serializes an object to a dictionary or JSON string.

    Args:
        obj (object): The object to serialize.
        exclude_methods (bool): If True, excludes methods from the serialization. Defaults to False.
        to_json (bool): If True, returns the serialized object as a JSON string. Defaults to False.

    Returns:
        dict or str: The serialized object as a dictionary or JSON string.
    """
    if obj is None:
        return None
    if force_string:
        return str(obj)
    try:
        obj_dict = {}

        for attr in dir(obj):
            if exclude_methods and callable(getattr(obj, attr)):
                continue
            if not attr.startswith("__"):
                if to_string:
                    obj_dict[attr] = str(getattr(obj, attr))
                else:
                    obj_dict[attr] = getattr(obj, attr)

        if to_json:
            return json.dumps(obj_dict)

        return obj_dict

    except Exception as e:
        return {"Error serializing object": str(e)}


def convert_size(size_in_bytes: int) -> str:
    """Converte tamanho em bytes para formato legível (KB, MB, GB)"""
    if size_in_bytes == 0:
        return ""

    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_in_bytes)
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    return f"{size:.1f} {units[unit_index]}"


def get_file_type(filename: str) -> str:
    """Determina o tipo do arquivo baseado na extensão"""
    _, ext = os.path.splitext(filename.lower())
    return ext


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


def _serialize_value(value: Any) -> Union[float, str, list, Dict[str, Any]]:
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
    except Exception as e:
        logger.warning(f"Error serializing value {value}: {e}")
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
    multi_level_attr: Optional[str] = None,
    method_params: Optional[Dict[str, Any]] = None,
    convert_type: Optional[str] = "str",
    float_precision: Optional[int] = 1,
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

        if hasattr(attr, "value") and multi_level_attr is None:
            # If the attribute is an Enum, return its value
            return attr.value

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

        # Apply type conversion if specified (NEW FUNCTIONALITY)
        if convert_type and convert_type != "auto":
            converted_value = serialize_with_type_conversion(
                value=value,
                target_type=convert_type,
                precision=float_precision,
                default=default,
            )
            # If conversion failed, fall back to original behavior
            if converted_value == default and value != default:
                logger.warning(
                    f"Type conversion failed for {attribute_name}, using original serialization"
                )
                rasterized_value = _serialize_value(value)
                return rasterized_value if rasterized_value is not None else default
            return converted_value

        # Serialize the value (ORIGINAL BEHAVIOR - UNCHANGED)
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


def serialize_with_type_conversion(
    value: Any, target_type: str, precision: Optional[int] = None, default: Any = None
) -> Any:
    """
    Serialize a value with dynamic type conversion.

    Args:
        value: The value to serialize
        target_type: Type to convert to ('int', 'float', 'str', 'datetime', 'date', 'bool')
        precision: Precision for float conversion (default: 2)
        default: Default value if conversion fails

    Returns:
        Converted value or default if conversion fails

    Examples:
        serialize_with_type_conversion(123.456, 'float', precision=2) -> 123.46
        serialize_with_type_conversion(123.456, 'int') -> 123
        serialize_with_type_conversion('2024-01-15', 'datetime') -> '2024-01-15T00:00:00'
    """
    try:
        if value is None:
            return default

        # Handle different target types
        if target_type == "int":
            return _convert_to_int(value, default)
        elif target_type == "float":
            return _convert_to_float(value, precision, default)
        elif target_type == "str":
            return _convert_to_string(value, default)
        elif target_type == "datetime":
            return _convert_to_datetime(value, default)
        elif target_type == "date":
            return _convert_to_date(value, default)
        elif target_type == "bool":
            return _convert_to_bool(value, default)
        else:
            logger.warning(f"Unsupported target type: {target_type}")
            return default

    except Exception as e:
        logger.warning(f"Error converting {value} to {target_type}: {e}")
        return default


def _convert_to_int(value: Any, default: Any = None) -> Any:
    """Convert value to integer without truncation."""
    try:
        if isinstance(value, (int, float)):
            # Use round() to avoid truncation for floats
            return int(round(value))
        elif isinstance(value, str):
            # Handle string numbers with proper rounding
            float_val = float(value)
            return int(round(float_val))
        else:
            # Try to convert through float first
            float_val = float(value)
            return int(round(float_val))
    except (ValueError, TypeError):
        return default


def _convert_to_float(
    value: Any, precision: Optional[int] = 2, default: Any = None
) -> Any:
    """Convert value to float with specified precision."""
    try:
        if isinstance(value, (int, float)):
            float_val = float(value)
        elif isinstance(value, str):
            float_val = float(value)
        else:
            float_val = float(value)

        # Apply precision if specified
        if precision is not None:
            return round(float_val, precision)
        return float_val
    except (ValueError, TypeError):
        return default


def _convert_to_string(value: Any, default: Any = None) -> Any:
    """Convert value to string."""
    try:
        return str(value)
    except Exception:
        return default


def _convert_to_datetime(value: Any, default: Any = None) -> Any:
    """Convert value to datetime string."""
    try:
        import datetime

        if isinstance(value, datetime.datetime):
            return value.isoformat()
        elif isinstance(value, datetime.date):
            return datetime.datetime.combine(value, datetime.time.min).isoformat()
        elif isinstance(value, str):
            # Try to parse common datetime formats
            for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    dt = datetime.datetime.strptime(value, fmt)
                    return dt.isoformat()
                except ValueError:
                    continue
            # If no format matches, return as string
            return value
        else:
            return str(value)
    except Exception:
        return default


def _convert_to_date(value: Any, default: Any = None) -> Any:
    """Convert value to date string."""
    try:
        import datetime

        if isinstance(value, datetime.date):
            return value.isoformat()
        elif isinstance(value, datetime.datetime):
            return value.date().isoformat()
        elif isinstance(value, str):
            # Try to parse common date formats
            for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    dt = datetime.datetime.strptime(value, fmt)
                    return dt.date().isoformat()
                except ValueError:
                    continue
            # If no format matches, return as string
            return value
        else:
            return str(value)
    except Exception:
        return default


def _convert_to_bool(value: Any, default: Any = None) -> Any:
    """Convert value to boolean."""
    try:
        if isinstance(value, bool):
            return value
        elif isinstance(value, (int, float)):
            return bool(value)
        elif isinstance(value, str):
            lower_val = value.lower()
            if lower_val in ("true", "1", "yes", "on"):
                return True
            elif lower_val in ("false", "0", "no", "off"):
                return False
            else:
                return bool(value)
        else:
            return bool(value)
    except Exception:
        return default


def safe_extract_attribute_with_type(
    obj: Any,
    attribute_name: str,
    target_type: str = "float",
    precision: Optional[int] = None,
    default: Any = None,
    multi_level_attr: Optional[str] = None,
    method_params: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Safely extract an attribute with type conversion.

    Args:
        obj: Object to extract attribute from
        attribute_name: Name of the attribute to extract
        target_type: Type to convert to ('int', 'float', 'str', 'datetime', 'date', 'bool')
        precision: Precision for float conversion
        default: Default value if extraction/conversion fails
        multi_level_attr: If provided, extract this attribute from the result
        method_params: Dictionary of parameters to pass to method if it's callable

    Returns:
        Extracted and converted attribute value or default
    """
    try:
        # Use the existing function with type conversion parameters
        return safe_extract_attribute(
            obj=obj,
            attribute_name=attribute_name,
            default=default,
            multi_level_attr=multi_level_attr,
            method_params=method_params,
            convert_type=target_type,
            float_precision=precision,
        )

    except Exception as e:
        logger.warning(f"Error extracting {attribute_name} with type conversion: {e}")
        return default


if __name__ == "__main__":
    pass
