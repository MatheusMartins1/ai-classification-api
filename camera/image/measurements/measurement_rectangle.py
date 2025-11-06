"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva.
No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

from typing import Optional, Dict, Any, Tuple
from camera.image.measurements.measurement_shape import MeasurementShapeManager


class MeasurementRectangle(MeasurementShapeManager):
    """Manages rectangular measurement areas in FLIR images."""

    def __init__(self, camera: Any, x: int, y: int, width: int, height: int) -> None:
        """
        Initialize a rectangular measurement area.

        Args:
            camera: Camera instance
            x: X coordinate of top-left corner
            y: Y coordinate of top-left corner
            width: Width of rectangle
            height: Height of rectangle
        """
        super().__init__(camera)
        self._setup_rectangle(x, y, width, height)

    def _setup_rectangle(self, x: int, y: int, width: int, height: int) -> None:
        """Create and configure the rectangular measurement."""
        try:
            # Create rectangle using Atlas SDK
            self._shape = self._camera.image_obj_thermal.Measurements.AddRectangle(
                x, y, width, height
            )
            self.logger.info(
                f"Created measurement rectangle at ({x},{y}) {width}x{height}"
            )
        except Exception as e:
            self.logger.error(f"Error creating measurement rectangle: {e}")

    @property
    def bounds(self) -> Optional[Tuple[int, int, int, int]]:
        """Get the rectangle bounds (x, y, width, height)."""
        try:
            if self._shape:
                return (
                    self._shape.X,
                    self._shape.Y,
                    self._shape.Width,
                    self._shape.Height,
                )
        except Exception as e:
            self.logger.error(f"Error getting rectangle bounds: {e}")
        return None

    @bounds.setter
    def bounds(self, values: Tuple[int, int, int, int]) -> None:
        """
        Set the rectangle bounds.

        Args:
            values: Tuple of (x, y, width, height)
        """
        try:
            if self._shape and len(values) == 4:
                x, y, width, height = values
                self._shape.X = x
                self._shape.Y = y
                self._shape.Width = width
                self._shape.Height = height
        except Exception as e:
            self.logger.error(f"Error setting rectangle bounds: {e}")

    def to_string(self) -> Dict[str, Any]:
        """Convert rectangle properties to a dictionary format."""
        base_props = super().to_string()
        base_props.update({"bounds": self.bounds})
        return base_props
