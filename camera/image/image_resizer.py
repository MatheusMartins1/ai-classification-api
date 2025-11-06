# NEXT: Implement image resizer class
# https://cursor.com/agents?selectedBcId=bc-35e27888-6c3f-43c4-8727-5bdc7ef2a287

"""
Developer: Matheus Martins da Silva
Creation Date: 08/2025
Description: Image resizer for thermal camera images with pixel mapping
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

import numpy as np
import cv2
from typing import Tuple, Dict, Optional
import logging


class ThermalImageResizer:
    """
    Handles resizing of thermal images while maintaining pixel correspondence.

    This class is specifically designed for thermal camera images where
    precise pixel mapping is crucial for temperature measurements and analysis.
    """

    def __init__(self, target_width: int = 1920, target_height: int = 1080):
        """
        Initialize the thermal image resizer.

        Args:
            target_width: Target width for resized images (default: 1920 for 1080p)
            target_height: Target height for resized images (default: 1080 for 1080p)
        """
        self.target_width = target_width
        self.target_height = target_height
        self.logger = logging.getLogger(__name__)

        # Store original dimensions for mapping
        self.original_width = None
        self.original_height = None

        # Scaling factors
        self.scale_x = None
        self.scale_y = None

    def set_original_dimensions(self, width: int, height: int):
        """
        Set the original image dimensions for pixel mapping calculations.

        Args:
            width: Original image width
            height: Original image height
        """
        self.original_width = width
        self.original_height = height

        # Calculate scaling factors
        self.scale_x = self.target_width / width
        self.scale_y = self.target_height / height

        # self.logger.info(f"Original dimensions: {width}x{height}")
        # self.logger.info(f"Target dimensions: {self.target_width}x{self.target_height}")
        # self.logger.info(f"Scale factors: X={self.scale_x:.3f}, Y={self.scale_y:.3f}")

    def resize_image(
        self, image: np.ndarray, interpolation: int = cv2.INTER_LINEAR
    ) -> np.ndarray:
        """
        Resize the image to target dimensions.

        Args:
            image: Input image as numpy array
            interpolation: OpenCV interpolation method (default: INTER_LINEAR)

        Returns:
            Resized image as numpy array
        """
        if image is None:
            return None

        # Set original dimensions if not set
        if self.original_width is None:
            height, width = image.shape[:2]
            self.set_original_dimensions(width, height)

        # Resize image
        resized = cv2.resize(
            image, (self.target_width, self.target_height), interpolation=interpolation
        )

        return resized

    def map_coordinates(self, x: int, y: int) -> Tuple[int, int]:
        """
        Map coordinates from original image to resized image.

        Args:
            x: X coordinate in original image
            y: Y coordinate in original image

        Returns:
            Tuple of (x, y) coordinates in resized image
        """
        if self.scale_x is None or self.scale_y is None:
            raise ValueError(
                "Original dimensions not set. Call set_original_dimensions() first."
            )

        # Map coordinates
        mapped_x = int(x * self.scale_x)
        mapped_y = int(y * self.scale_y)

        return mapped_x, mapped_y

    def map_coordinates_reverse(self, x: int, y: int) -> Tuple[int, int]:
        """
        Map coordinates from resized image back to original image.

        Args:
            x: X coordinate in resized image
            y: Y coordinate in resized image

        Returns:
            Tuple of (x, y) coordinates in original image
        """
        if self.scale_x is None or self.scale_y is None:
            raise ValueError(
                "Original dimensions not set. Call set_original_dimensions() first."
            )

        # Reverse map coordinates
        original_x = int(x / self.scale_x)
        original_y = int(y / self.scale_y)

        return original_x, original_y

    def map_measurement(self, measurement: Dict) -> Dict:
        """
        Map measurement coordinates from original to resized image.

        Args:
            measurement: Dictionary containing measurement data with coordinates

        Returns:
            Dictionary with mapped coordinates
        """
        mapped_measurement = measurement.copy()

        # Map different types of measurements
        if "x" in measurement and "y" in measurement:
            # Spot measurement
            mapped_x, mapped_y = self.map_coordinates(
                measurement["x"], measurement["y"]
            )
            mapped_measurement["x"] = mapped_x
            mapped_measurement["y"] = mapped_y

        elif (
            "x1" in measurement
            and "y1" in measurement
            and "x2" in measurement
            and "y2" in measurement
        ):
            # Line or rectangle measurement
            mapped_x1, mapped_y1 = self.map_coordinates(
                measurement["x1"], measurement["y1"]
            )
            mapped_x2, mapped_y2 = self.map_coordinates(
                measurement["x2"], measurement["y2"]
            )

            mapped_measurement["x1"] = mapped_x1
            mapped_measurement["y1"] = mapped_y1
            mapped_measurement["x2"] = mapped_x2
            mapped_measurement["y2"] = mapped_y2

        elif "center_x" in measurement and "center_y" in measurement:
            # Ellipse or other centered measurements
            mapped_center_x, mapped_center_y = self.map_coordinates(
                measurement["center_x"], measurement["center_y"]
            )
            mapped_measurement["center_x"] = mapped_center_x
            mapped_measurement["center_y"] = mapped_center_y

            # Map radius if present
            if "radius_x" in measurement and "radius_y" in measurement:
                mapped_measurement["radius_x"] = int(
                    measurement["radius_x"] * self.scale_x
                )
                mapped_measurement["radius_y"] = int(
                    measurement["radius_y"] * self.scale_y
                )

        return mapped_measurement

    def get_mapping_info(self) -> Dict:
        """
        Get information about the current mapping configuration.

        Returns:
            Dictionary with mapping information
        """
        return {
            "original_dimensions": (self.original_width, self.original_height),
            "target_dimensions": (self.target_width, self.target_height),
            "scale_factors": (self.scale_x, self.scale_y),
            "mapping_ready": self.scale_x is not None and self.scale_y is not None,
        }


class ThermalImageProcessor:
    """
    High-level processor for thermal images with resize capabilities.
    """

    def __init__(self, target_width: int = 1920, target_height: int = 1080):
        """
        Initialize the thermal image processor.

        Args:
            target_width: Target width for resized images
            target_height: Target height for resized images
        """
        self.resizer = ThermalImageResizer(target_width, target_height)
        self.logger = logging.getLogger(__name__)

    def process_image(
        self,
        image: np.ndarray,
        resize: bool = True,
        interpolation: int = cv2.INTER_LINEAR,
    ) -> Tuple[np.ndarray, Dict]:
        """
        Process a thermal image with optional resizing.

        Args:
            image: Input thermal image
            resize: Whether to resize the image
            interpolation: Interpolation method for resizing

        Returns:
            Tuple of (processed_image, mapping_info)
        """
        if image is None:
            return None, {}

        # Get original dimensions
        height, width = image.shape[:2]

        if resize:
            # Set original dimensions for mapping
            self.resizer.set_original_dimensions(width, height)

            # Resize image
            processed_image = self.resizer.resize_image(image, interpolation)

            # Get mapping information
            mapping_info = self.resizer.get_mapping_info()

            self.logger.info(
                f"Processed image: {width}x{height} -> {self.resizer.target_width}x{self.resizer.target_height}"
            )

            return processed_image, mapping_info
        else:
            # Return original image with basic info
            self.resizer.set_original_dimensions(width, height)
            mapping_info = self.resizer.get_mapping_info()
            return image, mapping_info

    def map_measurements(self, measurements: list) -> list:
        """
        Map a list of measurements to resized coordinates.

        Args:
            measurements: List of measurement dictionaries

        Returns:
            List of measurements with mapped coordinates
        """
        if not self.resizer.get_mapping_info()["mapping_ready"]:
            self.logger.warning("Mapping not ready. Call process_image() first.")
            return measurements

        mapped_measurements = []
        for measurement in measurements:
            mapped_measurement = self.resizer.map_measurement(measurement)
            mapped_measurements.append(mapped_measurement)

        return mapped_measurements

    def get_resizer(self) -> ThermalImageResizer:
        """
        Get the underlying resizer instance.

        Returns:
            ThermalImageResizer instance
        """
        return self.resizer
