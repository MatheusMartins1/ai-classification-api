"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva.
"""

from typing import Optional, Dict, Any
from threading import Lock


class MeasurementParameters:
    """Manages measurement parameters for FLIR measurements."""

    def __init__(self, camera: Any) -> None:
        """
        Initialize measurement parameters.

        Args:
            camera: Camera instance that provides access to thermal parameters
        """
        self._camera = camera
        self.logger = camera.logger
        self._lock = camera.service_lock

        # Instead of creating properties, we'll use methods
        self._image = camera.image_obj_thermal

    def get_emissivity(self) -> Optional[float]:
        """Get the emissivity value from the camera."""
        try:
            with self._lock:
                return self._image.Measurements.RadiometricSettings.Distance.Emissivity
        except Exception as e:
            self.logger.error(f"Error getting emissivity: {e}")
            return None

    def set_emissivity(self, value: float) -> None:
        """Set the emissivity value in the camera."""
        try:
            if not 0.0 <= value <= 1.0:
                raise ValueError("Emissivity must be between 0.0 and 1.0")

            with self._lock:
                self._image.Measurements.RadiometricSettings.Distance.Emissivity = value
                self.logger.info(f"Emissivity set to {value}")
        except Exception as e:
            self.logger.error(f"Error setting emissivity: {e}")

    def get_distance(self) -> Optional[float]:
        """Get the measurement distance from the camera."""
        try:
            with self._lock:
                return self._image.Measurements.RadiometricSettings.Distance.Distance
        except Exception as e:
            self.logger.error(f"Error getting distance: {e}")
            return None

    def set_distance(self, value: float) -> None:
        """Set the measurement distance in the camera."""
        try:
            if value < 0:
                raise ValueError("Distance must be non-negative")

            with self._lock:
                self._image.Measurements.RadiometricSettings.Distance.Distance = value
                self.logger.info(f"Distance set to {value}")
        except Exception as e:
            self.logger.error(f"Error setting distance: {e}")

    def to_string(self) -> Dict[str, Any]:
        """Convert current parameters to a dictionary format."""
        return {"emissivity": self.get_emissivity(), "distance": self.get_distance()}
