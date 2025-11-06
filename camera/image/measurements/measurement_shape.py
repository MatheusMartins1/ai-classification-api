"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva.
No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

import os
from typing import Any, Dict, Literal, Optional

import clr

from config.settings import settings

# Add the path to the directory containing the compiled DLL
dll_path = os.path.join(settings.BASE_DIR, "ThermalCameraLibrary")

clr.AddReference(os.path.join(dll_path, "ThermalCamera.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Live.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Image.dll"))
clr.AddReference("System")
clr.AddReference("System.Drawing")

import Flir.Atlas.Image as Image  # type: ignore
import System  # type: ignore
from System.Drawing import Point, Rectangle  # type: ignore


class MeasurementShapeManager:
    """Base class for all measurement shapes in FLIR Atlas SDK."""

    def __init__(self, _camera: Any) -> None:
        """
        Initialize MeasurementShape manager.

        Args:
            camera: Camera instance that provides access to the thermal image
        """
        self._camera = _camera
        self.logger = _camera.logger
        self._image = (
            _camera.image_obj_thermal
            if _camera.image_obj_thermal
            else _camera.image_obj_visual
        )
        self._shape = None
        self._parameters = None

    def create_or_update_rectangle(
        self, config: dict, operation_type: Literal["create", "update"] = "create"
    ) -> Optional[Image.Measurements.MeasurementRectangle]:
        """
        Create or update a MeasurementRectangle shape.

        Args:
            config (dict): Configuration containing:
                - x, y: location coordinates
                - width, height: dimensions
                - hot_spot_enabled: enable hot spot (optional)
                - cold_spot_enabled: enable cold spot (optional)
                - average_enabled: enable average (optional)
                - area_enabled: enable area calculation (optional)
            operation_type (str): "create" for new measurement, "update" for existing

        Returns:
            Optional[Image.Measurements.MeasurementRectangle]: Rectangle measurement object or None if failed
        """
        try:
            # Set basic properties
            x = int(config.get("x", 0))
            y = int(config.get("y", 0))
            width = int(config.get("width", 100))
            height = int(config.get("height", 100))

            if operation_type == "create":
                # Create new rectangle measurement
                shape = Rectangle(x, y, width, height)
                rectangle = self._image.Measurements.Add(shape)
            else:
                # Update existing rectangle - find by ID or use provided measurement object
                measurement_id = config.get("id")
                if not measurement_id:
                    self.logger.error("Measurement ID required for update operation")
                    return None

                # Find existing measurement and update properties
                rectangle = self._find_measurement_by_id(measurement_id)
                if not rectangle:
                    self.logger.error(f"Measurement with ID {measurement_id} not found")
                    return None

            # Configure measurement properties (for both create and update)
            if "hot_spot_enabled" in config:
                rectangle.IsHotSpotEnabled = config["hot_spot_enabled"]
                if config.get("hot_spot_marker_visible") is not None:
                    rectangle.IsHotSpotMarkerVisible = config["hot_spot_marker_visible"]

            if "cold_spot_enabled" in config:
                rectangle.IsColdSpotEnabled = config["cold_spot_enabled"]
                if config.get("cold_spot_marker_visible") is not None:
                    rectangle.IsColdSpotMarkerVisible = config[
                        "cold_spot_marker_visible"
                    ]

            if "average_enabled" in config:
                rectangle.IsAverageEnabled = config["average_enabled"]

            if "area_enabled" in config:
                rectangle.IsAreaEnabled = config["area_enabled"]

            # Update position and dimensions for both create and update
            if hasattr(rectangle, "Location"):
                rectangle.Location = Point(x, y)
            if hasattr(rectangle, "Width"):
                rectangle.Width = width
            if hasattr(rectangle, "Height"):
                rectangle.Height = height

            # Update name if provided
            if "name" in config:
                rectangle.Name = config["name"]

            # Update active state if provided
            if "active" in config:
                rectangle.IsSilent = not config["active"]

            operation_text = "Updated" if operation_type == "update" else "Created"
            self.logger.debug(
                f"{operation_text} measurement rectangle at ({x},{y}), "
                f"w={width}, h={height}"
            )
            return rectangle

        except Exception as e:
            self.logger.error(f"Error {operation_type}ing measurement rectangle: {e}")
            return None

    def create_or_update_spot(
        self, config: dict, operation_type: Literal["create", "update"] = "create"
    ) -> Optional[Image.Measurements.MeasurementSpot]:
        """
        Create or update a MeasurementSpot shape.

        Args:
            config (dict): Configuration containing:
                - x, y: point coordinates
                - value_enabled: enable value display (optional)
                - marker_visible: enable marker visibility (optional)
            operation_type (str): "create" for new measurement, "update" for existing

        Returns:
            Optional[Image.Measurements.MeasurementSpot]: Spot measurement object or None if failed
        """
        try:
            # Set location
            x = int(config.get("x", 0))
            y = int(config.get("y", 0))

            if operation_type == "create":
                # Create new spot measurement
                shape = Point(x, y)
                spot = self._image.Measurements.Add(shape)
            else:
                # Update existing spot
                measurement_id = config.get("id")
                if not measurement_id:
                    self.logger.error("Measurement ID required for update operation")
                    return None

                spot = self._find_measurement_by_id(measurement_id)
                if not spot:
                    self.logger.error(f"Measurement with ID {measurement_id} not found")
                    return None

            # Configure properties (for both create and update)
            if "value_enabled" in config:
                spot.IsValueEnabled = config["value_enabled"]

            if "marker_visible" in config:
                spot.IsMarkerVisible = config["marker_visible"]

            # Update position for both create and update
            if hasattr(spot, "Point"):
                spot.Point = Point(x, y)

            # Update name if provided
            if "name" in config:
                spot.Name = config["name"]

            # Update active state if provided
            if "active" in config:
                spot.IsSilent = not config["active"]

            operation_text = "Updated" if operation_type == "update" else "Created"
            self.logger.debug(f"{operation_text} measurement spot at ({x},{y})")
            return spot

        except Exception as e:
            self.logger.error(f"Error {operation_type}ing measurement spot: {e}")
            return None

    def create_or_update_line(
        self, config: dict, operation_type: Literal["create", "update"] = "create"
    ) -> Optional[Image.Measurements.MeasurementLine]:
        """
        Create or update a MeasurementLine shape.

        Args:
            config (dict): Configuration containing x1, y1, x2, y2 coordinates
                where (x1,y1) is the start point and (x2,y2) is the end point
            operation_type (str): "create" for new measurement, "update" for existing

        Returns:
            Optional[Image.Measurements.MeasurementLine]: Line measurement object or None if failed
        """
        try:
            # Create points for line start and end
            x1 = int(config.get("x1", 0))
            y1 = int(config.get("y1", 0))
            x2 = int(config.get("x2", 100))
            y2 = int(config.get("y2", 100))

            start_point = Point(x1, y1)
            end_point = Point(x2, y2)

            if operation_type == "create":
                # Create new line measurement
                line = self._image.Measurements.Add(start_point, end_point)
            else:
                # Update existing line
                measurement_id = config.get("id")
                if not measurement_id:
                    self.logger.error("Measurement ID required for update operation")
                    return None

                line = self._find_measurement_by_id(measurement_id)
                if not line:
                    self.logger.error(f"Measurement with ID {measurement_id} not found")
                    return None

            # Configure properties (for both create and update)
            if "hot_spot_enabled" in config:
                line.IsHotSpotEnabled = config["hot_spot_enabled"]

            if "cold_spot_enabled" in config:
                line.IsColdSpotEnabled = config["cold_spot_enabled"]

            if "average_enabled" in config:
                line.IsAverageEnabled = config["average_enabled"]

            if "length_enabled" in config:
                line.IsLengthEnabled = config["length_enabled"]

            # Update position for both create and update
            if hasattr(line, "Start"):
                line.Start = start_point
            if hasattr(line, "End"):
                line.End = end_point

            # Update name if provided
            if "name" in config:
                line.Name = config["name"]

            # Update active state if provided
            if "active" in config:
                line.IsSilent = not config["active"]

            operation_text = "Updated" if operation_type == "update" else "Created"
            self.logger.debug(
                f"{operation_text} measurement line from ({start_point.X},{start_point.Y}) "
                f"to ({end_point.X},{end_point.Y})"
            )
            return line

        except Exception as e:
            self.logger.error(f"Error {operation_type}ing measurement line: {e}")
            return None

    def create_or_update_ellipse(
        self, config: dict, operation_type: Literal["create", "update"] = "create"
    ) -> Optional[Image.Measurements.MeasurementEllipse]:
        """
        Create or update a MeasurementEllipse shape.

        Args:
            config (dict): Configuration containing:
                - x, y: location coordinates
                - width, height: dimensions
                - hot_spot_enabled: enable hot spot (optional)
                - cold_spot_enabled: enable cold spot (optional)
                - average_enabled: enable average (optional)
                - area_enabled: enable area calculation (optional)
            operation_type (str): "create" for new measurement, "update" for existing

        Returns:
            Optional[Image.Measurements.MeasurementEllipse]: Ellipse measurement object or None if failed
        """
        try:
            if operation_type == "create":
                # Create new ellipse measurement object
                ellipse = Image.Measurements.MeasurementEllipse()
                self._image.Measurements.Add(ellipse)
            else:
                # Update existing ellipse
                measurement_id = config.get("id")
                if not measurement_id:
                    self.logger.error("Measurement ID required for update operation")
                    return None

                ellipse = self._find_measurement_by_id(measurement_id)
                if not ellipse:
                    self.logger.error(f"Measurement with ID {measurement_id} not found")
                    return None

            # Set basic properties (for both create and update)
            location = Point(int(config.get("x", 0)), int(config.get("y", 0)))
            width = int(config.get("width", 100))
            height = int(config.get("height", 100))

            ellipse.Location = location
            ellipse.Width = width
            ellipse.Height = height

            # Configure measurement properties (for both create and update)
            if "hot_spot_enabled" in config:
                ellipse.IsHotSpotEnabled = config["hot_spot_enabled"]
                if config.get("hot_spot_marker_visible") is not None:
                    ellipse.IsHotSpotMarkerVisible = config["hot_spot_marker_visible"]

            if "cold_spot_enabled" in config:
                ellipse.IsColdSpotEnabled = config["cold_spot_enabled"]
                if config.get("cold_spot_marker_visible") is not None:
                    ellipse.IsColdSpotMarkerVisible = config["cold_spot_marker_visible"]

            if "average_enabled" in config:
                ellipse.IsAverageEnabled = config["average_enabled"]

            if "area_enabled" in config:
                ellipse.IsAreaEnabled = config["area_enabled"]

            # Update name if provided
            if "name" in config:
                ellipse.Name = config["name"]

            # Update active state if provided
            if "active" in config:
                ellipse.IsSilent = not config["active"]

            operation_text = "Updated" if operation_type == "update" else "Created"
            self.logger.debug(
                f"{operation_text} measurement ellipse at ({location.X},{location.Y}), "
                f"w={width}, h={height}"
            )
            return ellipse

        except Exception as e:
            self.logger.error(f"Error {operation_type}ing measurement ellipse: {e}")
            return None

    def _find_measurement_by_id(self, measurement_id: str) -> Optional[Any]:
        """
        Find a measurement by its ID in the measurements collection.

        Args:
            measurement_id (str): The ID of the measurement to find

        Returns:
            Optional[Any]: The measurement object if found, None otherwise
        """
        try:
            measurements_enum = self._image.Measurements.GetEnumerator()
            while measurements_enum.MoveNext():
                current_measurement = measurements_enum.Current
                if hasattr(current_measurement, "Identity"):
                    if current_measurement.Identity.ToString() == measurement_id:
                        return current_measurement
            return None
        except Exception as e:
            self.logger.error(f"Error finding measurement by ID: {e}")
            return None

    # Legacy methods for backward compatibility
    def create_rectangle(
        self, config: dict
    ) -> Optional[Image.Measurements.MeasurementRectangle]:
        """Legacy method - use create_or_update_rectangle instead."""
        return self.create_or_update_rectangle(config, "create")

    def create_spot(self, config: dict) -> Optional[Image.Measurements.MeasurementSpot]:
        """Legacy method - use create_or_update_spot instead."""
        return self.create_or_update_spot(config, "create")

    def create_line(self, config: dict) -> Optional[Image.Measurements.MeasurementLine]:
        """Legacy method - use create_or_update_line instead."""
        return self.create_or_update_line(config, "create")

    def create_ellipse(
        self, config: dict
    ) -> Optional[Image.Measurements.MeasurementEllipse]:
        """Legacy method - use create_or_update_ellipse instead."""
        return self.create_or_update_ellipse(config, "create")

    def to_string(self) -> Dict[str, Any]:
        """Convert shape properties to a dictionary format."""
        return {}
