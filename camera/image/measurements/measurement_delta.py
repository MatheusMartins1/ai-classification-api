"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva.
"""

from typing import Optional, Dict, Any, List
from camera.image.measurements.measurement_shape import MeasurementShapeManager


class MeasurementDelta(MeasurementShapeManager):
    """Manages delta measurements in FLIR images."""

    def __init__(self, camera: Any, reference_points: List[Tuple[int, int]]) -> None:
        """
        Initialize a delta measurement.

        Args:
            camera: Camera instance
            reference_points: List of (x,y) coordinates for reference points
        """
        super().__init__(camera)
        self._setup_delta(reference_points)

    def _setup_delta(self, reference_points: List[Tuple[int, int]]) -> None:
        """Create and configure the delta measurement."""
        try:
            if len(reference_points) < 2:
                raise ValueError(
                    "Delta measurement requires at least 2 reference points"
                )

            self._shape = self._camera.image_obj_thermal.Measurements.AddDelta()

            # Add reference points
            for x, y in reference_points:
                self._shape.AddReferencePoint(x, y)

            self.logger.info(
                f"Created delta measurement with {len(reference_points)} points"
            )
        except Exception as e:
            self.logger.error(f"Error creating delta measurement: {e}")

    @property
    def reference_points(self) -> Optional[List[Tuple[int, int]]]:
        """Get all reference points."""
        try:
            if self._shape:
                return [(point.X, point.Y) for point in self._shape.ReferencePoints]
        except Exception as e:
            self.logger.error(f"Error getting reference points: {e}")
        return None

    def add_reference_point(self, x: int, y: int) -> None:
        """Add a new reference point."""
        try:
            if self._shape:
                self._shape.AddReferencePoint(x, y)
        except Exception as e:
            self.logger.error(f"Error adding reference point: {e}")

    def clear_reference_points(self) -> None:
        """Clear all reference points."""
        try:
            if self._shape:
                self._shape.ClearReferencePoints()
        except Exception as e:
            self.logger.error(f"Error clearing reference points: {e}")

    def to_string(self) -> Dict[str, Any]:
        """Convert delta properties to a dictionary format."""
        base_props = super().to_string()
        base_props.update({"reference_points": self.reference_points})
        return base_props
