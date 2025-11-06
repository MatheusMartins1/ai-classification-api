"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

import os
import threading
from typing import List, Optional, Tuple

import clr

from config.settings import settings

# Add the path to the directory containing the compiled DLL
dll_path = os.path.join(settings.BASE_DIR, "ThermalCameraLibrary")

clr.AddReference(os.path.join(dll_path, "ThermalCamera.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Live.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Image.dll"))
clr.AddReference("System")

import Flir.Atlas.Image as Image  # type: ignore

# Import the necessary classes from the assembly
import Flir.Atlas.Live as live  # type: ignore

from camera.image.resources.camera_info import CameraInfo
from camera.image.resources.compass_info import CompassInfo
from camera.image.resources.gas_quantification import GasQuantification

# Import resource classes
from camera.image.resources.gps_info import GPSInfo
from camera.image.resources.image_metadata import ImageMetadata
from camera.image.resources.statistics_info import StatisticsInfo
from camera.image.resources.thermal_parameters import ThermalParameters
from camera.image.resources.zoom_info import ZoomInfo
from camera.image.resources.zoom_settings import ZoomSettings
from camera.palettes.palettes import PaletteHandler


class ImageHandler:
    """
    Handles image manipulation operations for both thermal and visual images from Flir cameras.

    This class focuses solely on image manipulation (zoom, coordinates, etc.).
    For data extraction (GPS, camera info, thermal parameters, etc.), use DataExtractorService.

    Reference:
        https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/namespace_flir_1_1_atlas_1_1_image.html
    """

    def __init__(self, _camera):
        """
        Initialize the ImageHandler with camera instance.

        Args:
            _camera: Parent camera instance
        """
        self._camera = _camera
        self.logger = _camera.logger
        self._service_lock = _camera.service_lock

        self.is_thermal_image_supported = None
        self.is_visual_image_supported = None

        self.image_type = None
        self.image_event = None

        self.current_thermal_image = None
        self.current_visual_image = None

        self.image_list = []

        # Initialize image objects
        self.image_obj_thermal = _camera.image_obj_thermal
        self._visual_image = _camera.image_obj_visual

        # Image manipulation objects
        self.image_fff = None
        self.image_byte_array = None
        self.image_pixel_data = None
        self.image_embedded_photo = None
        self.image_blob = None
        self.image_visual = None

        # Initialize resource managers for image manipulation
        self.gps_info = GPSInfo(self._camera)
        self.compass_info = CompassInfo(self._camera)
        self.camera_info = CameraInfo(self._camera)
        self.thermal_parameters = ThermalParameters(self._camera)
        self.gas_quantification = GasQuantification(self._camera)
        self.statistics_info = StatisticsInfo(self._camera)
        self.image_metadata = ImageMetadata(self._camera)
        self.zoom_info = ZoomInfo(self._camera)
        self.zoom_settings = ZoomSettings(self._camera)
        self.palette_handler = PaletteHandler(self._camera)

        self.update_image()

    def update_image(self, thermal_image: Optional[Image.ThermalImage] = None):
        """
        Update the current thermal image and its associated resources.

        Args:
            thermal_image: Optional thermal image to update. If None, uses the current thermal image.
        """
        with self._service_lock:
            if thermal_image is None and self.image_obj_thermal is None:
                return

            thermal_image = (
                thermal_image
                if isinstance(thermal_image, Image.ThermalImage)
                else self.image_obj_thermal
            )

            # Update all resources with the new thermal image
            self.gps_info.update_info(thermal_image)
            self.compass_info.update_info(thermal_image)
            self.camera_info.update_info(thermal_image)
            self.thermal_parameters.update_info(thermal_image)
            self.gas_quantification.update_info(thermal_image)
            self.statistics_info.update_info(thermal_image)
            self.image_metadata.update_info(thermal_image)
            self.zoom_info.update_info(thermal_image)
            self.palette_handler.update_info(thermal_image)

            # Update zoom settings
            self.zoom_settings.update_settings()

    def zoom_out(self, adjustment: float = 1):
        """
        Zoom out the camera by decreasing factor by 0.5.
        Minimum factor is 1.0 (no zoom).
        """
        if self._camera:
            factor = self.zoom_settings.factor if self.zoom_settings.factor else 1
            new_factor = max(1.0, factor - adjustment)
            try:
                self._camera.image_obj_thermal.Zoom.Factor = new_factor
                self.zoom_settings.factor = new_factor
                self.logger.info(
                    f"Camera zoomed out. New factor: {self.zoom_settings.factor}"
                )
            except Exception as e:
                self.logger.error(e)

    def zoom_in(self, adjustment: float = 1):
        """
        Zoom in the camera by increasing factor by 0.5.
        """
        if self._camera:
            factor = self.zoom_settings.factor if self.zoom_settings.factor else 1
            new_factor = factor + adjustment
            try:
                self._camera.image_obj_thermal.Zoom.Factor = new_factor
                self.zoom_settings.factor = new_factor
                self.logger.info(
                    f"Camera zoomed in. New factor: {self.zoom_settings.factor}"
                )
            except Exception as e:
                self.logger.error(e)

    def get_thermal_values(self, x: int, y: int) -> Optional[float]:
        """Get temperature value at specified coordinates.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Temperature value or None if error occurs
        """
        try:
            if self.image_obj_thermal:
                return self.image_obj_thermal.GetValueFromPosition(x, y)
            return None
        except Exception as e:
            self.logger.error(f"Error getting thermal value: {e}")
            return None

    def to_json(self) -> dict:
        """
        Returns basic image properties in JSON format.
        For complete thermal data extraction, use DataExtractorService directly.

        Returns:
            dict: Basic image properties (manipulation-related only)
        """
        try:
            image = (
                self._visual_image
                if not self.image_obj_thermal
                else self.image_obj_thermal
            )

            if not image:
                return {"error": "No image available"}

            # Only include image manipulation related properties
            properties = {
                "image_manipulation": {
                    "zoom_settings": (
                        self.zoom_settings.to_string() if self.zoom_settings else None
                    ),
                    "current_zoom_factor": getattr(self.zoom_settings, "factor", None),
                },
                "image_basic_info": {
                    "width": getattr(image, "Width", None),
                    "height": getattr(image, "Height", None),
                    "format": getattr(image, "ImageFormat", None),
                    "bits_per_pixel": getattr(image, "BitsPerPixel", None),
                },
                "note": "For complete thermal data (GPS, camera info, thermal parameters, etc.), use DataExtractorService",
            }

            return properties

        except Exception as e:
            self.logger.error(f"Error generating image JSON: {e}")
            return {"error": str(e)}


"""
# TODO: Implement classes:https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/class_flir_1_1_atlas_1_1_image_1_1_thermal_image.html#adf29867b6fde971760aee1906afec94f

PaletteManager 	PaletteManager[get]
 	Gets the palette object.
 
Palette 	Palette[get, set]
 	Handle palette selections.


ColorDistribution 	ColorDistribution[get, set]
 	Gets or sets the Thermal image color distribution.
 
Calculator 	ThermalMeasurements[get]
 	Calculate advanced measurements.
 
ImageStatistics 	Statistics[get]
 	Gets the image results ImageStatistics
 
ImageParameters 	ThermalParameters[get, protected set]
 	Gets the image object parameters i.e. emissivity, distance etc.
 

Histogram 	Histogram[get]
 	Gets the image Histogram.
 
TriggerData 	Trigger[get]
 	Gets the trigger settings for this image.
 
Scale 	Scale[get, set]
 	Gets the scale object.
 
 
Fusion.Fusion 	Fusion[get, protected set]
 	Gets the Fusion object.
 
SensorsCollection 	SensorsCollection[get]
 	Gets a collection of sensor data objects.
 

"""
"""
    # TODO: implement methods - https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/class_flir_1_1_atlas_1_1_image_1_1_thermal_image.html
    # GetEmissivityFromValue
    # GetSignalFromOutput

    TemperatureUnit 	TemperatureUnit[get, set]
 	Gets or sets the temperature unit and will propagate a TemperatureUnitChanged event when changed.
 
    DistanceUnit 	DistanceUnit[get, set]
        Gets or sets the distance unit.
"""
