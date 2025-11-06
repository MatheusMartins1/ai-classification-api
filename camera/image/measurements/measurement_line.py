"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva.
"""

from typing import Optional, Dict, Any, Tuple
from camera.image.measurements.measurement_shape import MeasurementShapeManager


class MeasurementLine(MeasurementShapeManager):
    """Manages line measurement areas in FLIR images."""

    def __init__(self, camera: Any, x1: int, y1: int, x2: int, y2: int) -> None:
        """
        Initialize a line measurement.

        Args:
            camera: Camera instance
            x1: X coordinate of start point
            y1: Y coordinate of start point
            x2: X coordinate of end point
            y2: Y coordinate of end point
        """
        super().__init__(camera)
        self._setup_line(x1, y1, x2, y2)

    def _setup_line(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Create and configure the line measurement."""
        try:
            self._shape = self._camera.image_obj_thermal.Measurements.AddLine(
                x1, y1, x2, y2
            )
            self.logger.info(
                f"Created measurement line from ({x1},{y1}) to ({x2},{y2})"
            )
        except Exception as e:
            self.logger.error(f"Error creating measurement line: {e}")

    @property
    def start_point(self) -> Optional[Tuple[int, int]]:
        """Get the line start point (x1, y1)."""
        try:
            if self._shape:
                return (self._shape.X1, self._shape.Y1)
        except Exception as e:
            self.logger.error(f"Error getting line start point: {e}")
        return None

    @property
    def end_point(self) -> Optional[Tuple[int, int]]:
        """Get the line end point (x2, y2)."""
        try:
            if self._shape:
                return (self._shape.X2, self._shape.Y2)
        except Exception as e:
            self.logger.error(f"Error getting line end point: {e}")
        return None

    def set_points(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Set both start and end points of the line."""
        try:
            if self._shape:
                self._shape.X1 = x1
                self._shape.Y1 = y1
                self._shape.X2 = x2
                self._shape.Y2 = y2
        except Exception as e:
            self.logger.error(f"Error setting line points: {e}")

    def to_string(self) -> Dict[str, Any]:
        """Convert line properties to a dictionary format."""
        base_props = super().to_string()
        base_props.update(
            {"start_point": self.start_point, "end_point": self.end_point}
        )
        return base_props
