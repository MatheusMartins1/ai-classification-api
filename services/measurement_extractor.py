"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Service for extracting measurement data from FLIR thermal images.
Based on flyr library measurement_info module.
Reference: https://bitbucket.org/nimmerwoner/flyr/src/master/flyr/measurement_info.py
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

from typing import Any, List, Optional

import numpy as np  # type: ignore

from models.thermal_data import Measurement
from utils import temperature_calculations
from utils.LoggerConfig import LoggerConfig
from utils.object_handler import extract_all_attributes

logger = LoggerConfig.add_file_logger(
    name="measurement_extractor",
    filename=None,
    dir_name=None,
    prefix="measurement",
    level_name="INFO",
)


class MeasurementExtractor:
    """
    Service class for extracting measurement data from thermograms.
    Single responsibility: Extract and parse measurement information.
    """

    # Mapping of FLIR tool types to standard measurement types
    # Based on flyr.measurement_info.Tool enum
    TOOL_TYPE_MAPPING = {
        "SPOT": "SPOT",
        "AREA": "AREA",
        "LINE": "LINE",
        "RECTANGLE": "RECTANGLE",
        "ELLIPSE": "ELLIPSE",
        "CIRCLE": "CIRCLE",
        "POLYGON": "POLYGON",
    }

    def extract_measurements(
        self, thermogram: Any
    ) -> List[Measurement]:
        """
        Extract all measurements from a thermogram with temperature statistics.

        Args:
            thermogram: Thermogram object from flyr library

        Returns:
            List of Measurement objects with temperature statistics
        """
        measurements: List[Measurement] = []

        try:
            # Check if thermogram has measurements attribute
            if not hasattr(thermogram, "measurements"):
                logger.info("Thermogram has no measurements attribute")
                return measurements

            raw_measurements = thermogram.measurements

            # Handle None or empty measurements
            if raw_measurements is None or len(raw_measurements) == 0:
                logger.info("No measurements found in thermogram")
                return measurements

            logger.info(f"Found {len(raw_measurements)} measurements in thermogram")

            # Get temperature array if not provided
            if hasattr(thermogram, "celsius"):
                celsius_array = thermogram.celsius

            # Extract each measurement
            for idx, raw_measurement in enumerate(raw_measurements):
                try:
                    measurement = self._parse_measurement(
                        raw_measurement, idx, celsius_array
                    )
                    if measurement:
                        measurements.append(measurement)
                except Exception as e:
                    logger.warning(f"Error parsing measurement {idx}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error extracting measurements: {e}")

        return measurements

    def _parse_measurement(
        self, raw_measurement: Any, index: int, celsius_array: Optional[np.ndarray]
    ) -> Optional[Measurement]:
        """
        Parse a single measurement from FLIR data with temperature statistics.

        Args:
            raw_measurement: Raw measurement object from flyr
            index: Index of the measurement
            celsius_array: Temperature matrix in Celsius

        Returns:
            Measurement object with temperature statistics or None if parsing fails
        """
        try:
            # Extract all attributes from the measurement object
            measurement_dict_raw = extract_all_attributes(
                raw_measurement, f"measurement_{index}"
            )

            # Ensure we have a dict
            measurement_dict: dict = (
                measurement_dict_raw if isinstance(measurement_dict_raw, dict) else {}
            )

            # Get measurement type from tool attribute
            tool_type = self._extract_tool_type(raw_measurement, measurement_dict)

            # Get label from measurement
            label = self._extract_label(raw_measurement, measurement_dict, index)

            # Get coordinates and dimensions
            params = self._extract_params(raw_measurement, measurement_dict)

            # Get color if available
            color = self._extract_color(raw_measurement, measurement_dict)

            # Extract temperature statistics from region
            temp_stats = self._extract_region_temperatures(
                params, tool_type if tool_type else "UNKNOWN", celsius_array
            )

            # Create Measurement object
            measurement = Measurement(
                type=tool_type,
                x=params.get("x"),
                y=params.get("y"),
                width=params.get("width"),
                height=params.get("height"),
                temperature=temp_stats.get("avg_temperature"),
                min_temperature=temp_stats.get("min_temperature"),
                max_temperature=temp_stats.get("max_temperature"),
                median_temperature=temp_stats.get("median_temperature"),
                std_deviation=temp_stats.get("std_deviation"),
                variance=temp_stats.get("variance"),
                percentile_25=temp_stats.get("percentile_25"),
                percentile_75=temp_stats.get("percentile_75"),
                percentile_90=temp_stats.get("percentile_90"),
                color=color,
                label=label,
                description=f"Measurement {index + 1}",
                notes=None,
            )

            logger.info(
                f"Parsed measurement {index}: type={tool_type}, label={label}, "
                f"avg_temp={temp_stats.get('avg_temperature'):.2f}°C"
            )

            return measurement

        except Exception as e:
            logger.error(f"Error parsing measurement {index}: {e}")
            return None

    def _extract_tool_type(
        self, raw_measurement: Any, measurement_dict: dict
    ) -> Optional[str]:
        """
        Extract and normalize tool type from measurement.
        Based on flyr.measurement_info.Measurement.tool attribute.

        Args:
            raw_measurement: Raw measurement object (flyr.measurement_info.Measurement)
            measurement_dict: Extracted measurement attributes

        Returns:
            Normalized tool type string
        """
        try:
            # Flyr measurement has .tool attribute which is a Tool enum
            if hasattr(raw_measurement, "tool"):
                tool = raw_measurement.tool
                # Tool enum has .name attribute
                if hasattr(tool, "name"):
                    tool_name = str(tool.name).upper()
                    return self.TOOL_TYPE_MAPPING.get(tool_name, tool_name)
                # Fallback to value
                elif hasattr(tool, "value"):
                    tool_name = str(tool.value).upper()
                    return self.TOOL_TYPE_MAPPING.get(tool_name, tool_name)

            # Try from dictionary
            if "tool" in measurement_dict:
                tool_name = str(measurement_dict["tool"]).upper()
                return self.TOOL_TYPE_MAPPING.get(tool_name, tool_name)

        except Exception as e:
            logger.warning(f"Error extracting tool type: {e}")

        return "UNKNOWN"

    def _extract_label(
        self, raw_measurement: Any, measurement_dict: dict, index: int
    ) -> str:
        """
        Extract label from measurement.

        Args:
            raw_measurement: Raw measurement object
            measurement_dict: Extracted measurement attributes
            index: Measurement index for default label

        Returns:
            Label string
        """
        try:
            # Try to get label attribute
            if hasattr(raw_measurement, "label"):
                label = str(raw_measurement.label)
                if label and label != "None":
                    return label

            # Try from dictionary
            if "label" in measurement_dict:
                label = str(measurement_dict["label"])
                if label and label != "None":
                    return label

        except Exception as e:
            logger.warning(f"Error extracting label: {e}")

        # Return default label
        return str(index + 1)

    def _extract_params(self, raw_measurement: Any, measurement_dict: dict) -> dict:
        """
        Extract coordinates and dimensions from measurement params.
        Based on flyr.measurement_info.Measurement.params attribute.

        Flyr params format:
        - SPOT: [x, y]
        - AREA/RECTANGLE: [x, y, width, height]
        - LINE: [x1, y1, x2, y2]
        - ELLIPSE/CIRCLE: [center_x, center_y, radius_x, radius_y]

        Args:
            raw_measurement: Raw measurement object (flyr.measurement_info.Measurement)
            measurement_dict: Extracted measurement attributes

        Returns:
            Dictionary with x, y, width, height
        """
        params: dict = {"x": None, "y": None, "width": None, "height": None}

        try:
            # Flyr measurement has .params attribute as a list
            if hasattr(raw_measurement, "params"):
                params_obj = raw_measurement.params

                # params is a list with different lengths based on tool type
                if isinstance(params_obj, (list, tuple)) and len(params_obj) > 0:
                    # All measurements have at least x, y
                    if len(params_obj) >= 2:
                        params["x"] = (
                            int(params_obj[0]) if params_obj[0] is not None else None
                        )
                        params["y"] = (
                            int(params_obj[1]) if params_obj[1] is not None else None
                        )

                    # AREA, RECTANGLE, LINE, ELLIPSE have 4 parameters
                    if len(params_obj) >= 4:
                        params["width"] = (
                            int(params_obj[2]) if params_obj[2] is not None else None
                        )
                        params["height"] = (
                            int(params_obj[3]) if params_obj[3] is not None else None
                        )

            # Fallback: Try from dictionary
            elif "params" in measurement_dict:
                params_data = measurement_dict["params"]
                if isinstance(params_data, (list, tuple)) and len(params_data) > 0:
                    if len(params_data) >= 2:
                        params["x"] = (
                            int(params_data[0]) if params_data[0] is not None else None
                        )
                        params["y"] = (
                            int(params_data[1]) if params_data[1] is not None else None
                        )
                    if len(params_data) >= 4:
                        params["width"] = (
                            int(params_data[2]) if params_data[2] is not None else None
                        )
                        params["height"] = (
                            int(params_data[3]) if params_data[3] is not None else None
                        )

        except Exception as e:
            logger.warning(f"Error extracting params: {e}")

        return params

    def _extract_temperature(
        self, raw_measurement: Any, measurement_dict: dict
    ) -> Optional[float]:
        """
        Extract temperature value from measurement.

        Args:
            raw_measurement: Raw measurement object
            measurement_dict: Extracted measurement attributes

        Returns:
            Temperature value in Celsius or None
        """
        try:
            # Try common temperature attributes
            temp_attrs = ["temperature", "temp", "value", "celsius"]

            for attr in temp_attrs:
                if hasattr(raw_measurement, attr):
                    temp = getattr(raw_measurement, attr)
                    if temp is not None:
                        return float(temp)

                if attr in measurement_dict:
                    temp = measurement_dict[attr]
                    if temp is not None:
                        return float(temp)

        except Exception as e:
            logger.warning(f"Error extracting temperature: {e}")

        return None

    def _extract_color(
        self, raw_measurement: Any, measurement_dict: dict
    ) -> Optional[str]:
        """
        Extract color from measurement.

        Args:
            raw_measurement: Raw measurement object
            measurement_dict: Extracted measurement attributes

        Returns:
            Color string or None
        """
        try:
            # Try to get color attribute
            if hasattr(raw_measurement, "color"):
                color = raw_measurement.color
                if color is not None:
                    return str(color)

            # Try from dictionary
            if "color" in measurement_dict:
                color = measurement_dict["color"]
                if color is not None:
                    return str(color)

        except Exception as e:
            logger.warning(f"Error extracting color: {e}")

        return None

    def _extract_region_temperatures(
        self, params: dict, tool_type: str, celsius_array: Optional[np.ndarray]
    ) -> dict:
        """
        Extract temperature statistics from measurement region.

        Args:
            params: Dictionary with x, y, width, height
            tool_type: Type of measurement tool
            celsius_array: Temperature matrix in Celsius

        Returns:
            Dictionary with temperature statistics
        """
        # Default empty statistics
        default_stats = {
            "avg_temperature": None,
            "min_temperature": None,
            "max_temperature": None,
            "median_temperature": None,
            "std_deviation": None,
            "variance": None,
            "percentile_25": None,
            "percentile_75": None,
            "percentile_90": None,
        }

        try:
            # Check if we have temperature array
            if celsius_array is None:
                logger.warning("No temperature array available for measurement")
                return default_stats

            # Get coordinates
            x = params.get("x")
            y = params.get("y")
            width = params.get("width")
            height = params.get("height")

            # Extract temperature region based on tool type
            if tool_type == "SPOT":
                # Single point measurement
                temp_region = self._extract_spot_temperature(x, y, celsius_array)
            elif tool_type in ["AREA", "RECTANGLE"]:
                # Rectangular area
                temp_region = self._extract_rectangle_temperature(
                    x, y, width, height, celsius_array
                )
            elif tool_type == "LINE":
                # Line measurement
                temp_region = self._extract_line_temperature(
                    x, y, width, height, celsius_array
                )
            elif tool_type in ["ELLIPSE", "CIRCLE"]:
                # Ellipse/Circle measurement
                temp_region = self._extract_ellipse_temperature(
                    x, y, width, height, celsius_array
                )
            else:
                logger.warning(
                    f"Unsupported tool type for temperature extraction: {tool_type}"
                )
                return default_stats

            # Calculate statistics if we have valid temperature data
            if temp_region is not None and len(temp_region) > 0:
                return {
                    "avg_temperature": temperature_calculations.get_average_from_temperature_array(
                        temp_region
                    ),
                    "min_temperature": temperature_calculations.get_min_from_temperature_array(
                        temp_region
                    ),
                    "max_temperature": temperature_calculations.get_max_from_temperature_array(
                        temp_region
                    ),
                    "median_temperature": temperature_calculations.get_median_from_temperature_array(
                        temp_region
                    ),
                    "std_deviation": temperature_calculations.get_standard_deviation_from_temperature_array(
                        temp_region
                    ),
                    "variance": temperature_calculations.get_variance_from_temperature_array(
                        temp_region
                    ),
                    "percentile_25": temperature_calculations.get_percentile_from_temperature_array(
                        temp_region, 25
                    ),
                    "percentile_75": temperature_calculations.get_percentile_from_temperature_array(
                        temp_region, 75
                    ),
                    "percentile_90": temperature_calculations.get_percentile_from_temperature_array(
                        temp_region, 90
                    ),
                }

        except Exception as e:
            logger.error(f"Error extracting region temperatures: {e}")

        return default_stats

    def _extract_spot_temperature(
        self, x: Optional[int], y: Optional[int], celsius_array: np.ndarray
    ) -> Optional[np.ndarray]:
        """Extract temperature for a single point."""
        try:
            if x is None or y is None:
                return None

            # Get image dimensions
            height, width = celsius_array.shape

            # Validate coordinates
            if 0 <= y < height and 0 <= x < width:
                # Return single temperature as array for consistency
                return np.array([celsius_array[y, x]])

        except Exception as e:
            logger.warning(f"Error extracting spot temperature: {e}")

        return None

    def _extract_rectangle_temperature(
        self,
        x: Optional[int],
        y: Optional[int],
        w: Optional[int],
        h: Optional[int],
        celsius_array: np.ndarray,
    ) -> Optional[np.ndarray]:
        """Extract temperatures for rectangular region."""
        try:
            if x is None or y is None or w is None or h is None:
                return None

            # Get image dimensions
            img_height, img_width = celsius_array.shape

            # Calculate bounds
            x1 = max(0, x)
            y1 = max(0, y)
            x2 = min(img_width, x + w)
            y2 = min(img_height, y + h)

            # Extract region
            if x2 > x1 and y2 > y1:
                region = celsius_array[y1:y2, x1:x2]
                return region.flatten()

        except Exception as e:
            logger.warning(f"Error extracting rectangle temperature: {e}")

        return None

    def _extract_line_temperature(
        self,
        x1: Optional[int],
        y1: Optional[int],
        x2: Optional[int],
        y2: Optional[int],
        celsius_array: np.ndarray,
    ) -> Optional[np.ndarray]:
        """Extract temperatures along a line."""
        try:
            if x1 is None or y1 is None or x2 is None or y2 is None:
                return None

            # Get image dimensions
            height, width = celsius_array.shape

            # Generate line points using Bresenham's algorithm
            num_points = max(abs(x2 - x1), abs(y2 - y1)) + 1
            x_coords = np.linspace(x1, x2, num_points).astype(int)
            y_coords = np.linspace(y1, y2, num_points).astype(int)

            # Filter valid coordinates
            valid_mask = (
                (x_coords >= 0)
                & (x_coords < width)
                & (y_coords >= 0)
                & (y_coords < height)
            )
            x_coords = x_coords[valid_mask]
            y_coords = y_coords[valid_mask]

            if len(x_coords) > 0:
                temperatures = celsius_array[y_coords, x_coords]
                return temperatures

        except Exception as e:
            logger.warning(f"Error extracting line temperature: {e}")

        return None

    def _extract_ellipse_temperature(
        self,
        center_x: Optional[int],
        center_y: Optional[int],
        radius_x: Optional[int],
        radius_y: Optional[int],
        celsius_array: np.ndarray,
    ) -> Optional[np.ndarray]:
        """Extract temperatures for ellipse/circle region."""
        try:
            if (
                center_x is None
                or center_y is None
                or radius_x is None
                or radius_y is None
            ):
                return None

            # Get image dimensions
            height, width = celsius_array.shape

            # Create meshgrid for ellipse mask
            y_grid, x_grid = np.ogrid[:height, :width]

            # Ellipse equation: ((x-cx)/rx)^2 + ((y-cy)/ry)^2 <= 1
            mask = (
                ((x_grid - center_x) / max(radius_x, 1)) ** 2
                + ((y_grid - center_y) / max(radius_y, 1)) ** 2
            ) <= 1

            # Extract temperatures within ellipse
            temperatures = celsius_array[mask]

            if len(temperatures) > 0:
                return temperatures

        except Exception as e:
            logger.warning(f"Error extracting ellipse temperature: {e}")

        return None
