"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva.
"""

from typing import Optional, Dict, Any, Tuple
from camera.image.measurements.measurement_shape import MeasurementShapeManager


class MeasurementEllipse(MeasurementShapeManager):
    """Manages elliptical measurement areas in FLIR images."""

    def __init__(self, camera: Any, x: int, y: int, width: int, height: int) -> None:
        """
        Initialize an elliptical measurement area.

        Args:
            camera: Camera instance
            x: X coordinate of center
            y: Y coordinate of center
            width: Width of ellipse
            height: Height of ellipse
        """
        super().__init__(camera)
        self._setup_ellipse(x, y, width, height)

    def _setup_ellipse(self, x: int, y: int, width: int, height: int) -> None:
        """Create and configure the elliptical measurement."""
        try:
            self._shape = self._camera.image_obj_thermal.Measurements.AddEllipse(
                x, y, width, height
            )
            self.logger.info(
                f"Created measurement ellipse at ({x},{y}) {width}x{height}"
            )
        except Exception as e:
            self.logger.error(f"Error creating measurement ellipse: {e}")

    @property
    def center(self) -> Optional[Tuple[int, int]]:
        """Get the ellipse center point (x, y)."""
        try:
            if self._shape:
                return (self._shape.CenterX, self._shape.CenterY)
        except Exception as e:
            self.logger.error(f"Error getting ellipse center: {e}")
        return None

    @property
    def dimensions(self) -> Optional[Tuple[int, int]]:
        """Get the ellipse dimensions (width, height)."""
        try:
            if self._shape:
                return (self._shape.Width, self._shape.Height)
        except Exception as e:
            self.logger.error(f"Error getting ellipse dimensions: {e}")
        return None

    def set_dimensions(self, width: int, height: int) -> None:
        """Set the ellipse dimensions."""
        try:
            if self._shape:
                self._shape.Width = width
                self._shape.Height = height
        except Exception as e:
            self.logger.error(f"Error setting ellipse dimensions: {e}")

    def set_center(self, x: int, y: int) -> None:
        """Set the ellipse center point."""
        try:
            if self._shape:
                self._shape.CenterX = x
                self._shape.CenterY = y
        except Exception as e:
            self.logger.error(f"Error setting ellipse center: {e}")

    def to_string(self) -> Dict[str, Any]:
        """Convert ellipse properties to a dictionary format."""
        base_props = super().to_string()
        base_props.update({"center": self.center, "dimensions": self.dimensions})
        return base_props
