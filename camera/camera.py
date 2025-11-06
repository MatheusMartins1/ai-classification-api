"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Description: This module manages the thermal camera, including initialization, device discovery, and thermal image handling.
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

import os
import clr
import sys
import time

from config.settings import settings
from typing import Optional, Any
import threading
import numpy as np
from PIL import Image as PILImage
import io
import datetime

from utils import object_handler
from camera.camera_locks import camera_locks

# Add the path to the directory containing the compiled DLL
dll_path = os.path.join(settings.BASE_DIR, "ThermalCameraLibrary")
# TODO: Check if this will break the app
sys.path.append(dll_path)

clr.AddReference(os.path.join(dll_path, "ThermalCamera.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Live.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Image.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Gigevision.dll"))
clr.AddReference("System")

# Import Flir SDK
import Flir.Atlas.Live as live  # type: ignore
import Flir.Atlas.Image as Image  # type: ignore
import Flir.Atlas.Gigevision as Gigevision  # type: ignore
import System  # type: ignore

# Import local modules
import camera.camera_connection as connection_manager
import camera.camera_events as event_manager
import camera.camera_logs as log_manager
import camera.camera_ui as ui_manager
import camera.controls.control as control_manager
import camera.camera_streaming as streaming_manager

import camera.image.alarms.alarm as alarm_handler
import camera.image.measurements.measurements as measurements_handler
import image.bitmap_handler as bitmap_handler
import camera.image.image as image_handler
import camera.image.image_resizer as image_resizer
import camera.image.image_extraction as image_extraction
import camera.palettes.palettes as palettes_handler


class CameraManager:
    """
    The CameraManager class manages the thermal camera, including initialization, device discovery, and thermal image handling.
    """

    # TODO: Implementar um singleton para a classe CameraManager
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """
        Create and return a new instance of the CameraManager class.

        This method implements the Singleton pattern, ensuring that only one instance
        of the CameraManager class is created. If an instance already exists, it returns
        the existing instance. The method is thread-safe, using a lock to prevent multiple
        threads from creating multiple instances simultaneously.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            CameraManager: The single instance of the CameraManager class.
        """
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(CameraManager, cls).__new__(
                        cls, *args, **kwargs
                    )
                    cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        """
        Initialize the CameraManager class.
        """
        if self.__initialized:
            return
        self.log_manager = log_manager.CameraLogManager(self)
        self.logger = self.log_manager.logger

        self.__initialized = True
        self.is_connected = False
        self.camera = None

        self._locks = camera_locks  # Adicionamos o gerenciador centralizado
        self.camera_lock = self._locks("camera")
        self.image_lock = self._locks("image")
        self.memory_lock = self._locks("memory")
        self.control_lock = self._locks("control")
        self.events_lock = self._locks("events")
        self.service_lock = self._locks("service")

        self.camera_ip = None
        self.camera_port = None
        self.camera_type = None

        self.fps = None
        self.width = None
        self.height = None
        self.camera_name = None
        self.camera_serial = None
        self.camera_article = None
        self.camera_device_identifier = None
        self.camera_streaming_format_name = None

        self.resize_image = False
        self.width_resized = None
        self.height_resized = None
        self.resize_mapping = None

        # TODO: get from Flir.Atlas.Image.CameraInformation - https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/class_flir_1_1_atlas_1_1_image_1_1_camera_information.html
        self.camera_model = None
        self.camera_serial_number = None
        self.camera_lens = None
        self.camera_fov = None
        self.camera_range = None

        self.security_parameters = None
        self.camera_device_info = None
        self.is_initialized = False
        self.is_image_initialized = False
        self.is_dual_streaming = None

        self.is_thermal_image_supported = None
        self.is_visual_image_supported = None
        self.image_bitmap_visual = None
        self.image_bitmap_thermal = None
        self.image_type = None
        self.image_obj_thermal = None
        self.image_fff = None
        self.image_byte = None
        self.image_obj_visual = None
        self.image_received = None
        self.image_event = None
        self.current_thermal_image = None
        self.current_visual_image = None
        self.current_thermal_image_resized = None
        self.current_visual_image_resized = None
        self.image_list = []
        self.connection_status = "Default"

        self.temperature_unit = "Celsius"
        self.temperature_unit_obj = None

        self.palette = None
        self.palette_name = None
        self.refresh_ui = False

        self.alarms = []
        self.measurements = []

        self.is_load_disabled = False

        self.event_manager = event_manager.CameraEventManager(self)
        self.camera_control = control_manager.CameraControl(self)
        self.connection_manager = connection_manager.CameraConnectionManager(self)

        # self.ui_manager = ui_manager.CameraUIManager(self)
        # TODO: Finish or remove
        self.streaming = streaming_manager.CameraStreaming(self)

        # Initilized later
        # TODO: change the initialization of the handlers, remove the None and add the handlers and modify de code to make a update()
        self.camera_image_handler = None
        self.alarms_handler = None
        self.measurements_handler = None
        self.image_service = None
        self.palettes_handler = None

        # TEST: if this is working
        self.image_processor = image_resizer.ThermalImageProcessor()
        
        # Image extraction handler
        self.image_extractor = image_extraction.ImageExtractor(self)

        self.is_image_ready = False
        #TODO: Change to a centralized event manager/ threading handler
        self._image_ready_event = threading.Event()

        # TODO: Implement the rest of the camera connection logic
        # self.video_quality = Flir.Atlas.Live.Discovery.VideoQuality #enum
        # self.interface = Flir.Atlas.Live.Discovery.Interface #enum

    # Legacy
    def get_logs(self):
        return self.log_manager.get_logs(self.log_manager.logs)

    def get_current_image(self, image_type: str = "thermal") -> Optional[np.ndarray]:
        """
        Get the current image in a thread-safe manner.

        Args:
            image_type: The type of image to retrieve ("thermal" or "visual")

        Returns:
            The current image, or None if extraction fails

        Raises:
            ValueError: If image_type is not supported
        """
        if self.camera is None:
            self.logger.info("Camera is not connected")
            return None

        # extract_image() handles its own .NET locks internally
        img = self.image_extractor.extract_image()
        
        if image_type == "thermal":
            return self.current_thermal_image
        elif image_type == "visual":
            return self.current_visual_image
        else:
            raise ValueError(f"Unsupported image type: {image_type}")

    def set_image_ready(self, ready: bool) -> None:
        """
        Set image ready state in a thread-safe manner.

        Args:
            ready (bool): True if images are ready for extraction
        """
        with self._locks("control"):
            self.is_image_ready = ready
            if ready:
                self._image_ready_event.set()
            else:
                self._image_ready_event.clear()
            self.logger.info(f"Image ready state changed to: {ready}")

    def wait_for_image_ready(self, timeout: float = 30.0) -> bool:
        """
        Wait until images are ready for extraction.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if images became ready, False if timeout
        """
        return self._image_ready_event.wait(timeout=timeout)

    def check_image_ready(self) -> bool:
        """
        Check if images are ready for extraction (thread-safe).

        Returns:
            bool: True if images are ready
        """
        with self._locks("control"):
            return self.is_image_ready

    def extract_image(self, image: Optional[Any] = None) -> Optional[np.ndarray]:
        """
        Get the current image from the camera.
        Delegates to ImageExtractor for image extraction.

        Args:
            image: Optional pre-loaded image object

        Returns:
            The current image from the camera as a numpy array, or None if extraction fails
        """
        return self.image_extractor.extract_image(image)

    def process_image(self, image):
        """
        Process the image and convert it to a format suitable for display.

        Args:
            image: The image to process.

        Returns:
            The processed image.
        """
        lock_acquired = False
        
        try:
            # Use TryEnterLock() for non-blocking lock acquisition
            if hasattr(image, "TryEnterLock"):
                lock_acquired = image.TryEnterLock()
                
                if not lock_acquired:
                    self.logger.warning("Could not acquire lock to process image")
                    return None

            img = image.Image

            # Convert the image to a numpy array if it's not already
            if not isinstance(img, np.ndarray):
                img = np.array(img)

            return img
            
        except System.AccessViolationException:
            self.logger.error("Access violation processing image - camera busy")
            return None
        except Exception as ex:
            self.logger.error(f"Erro ao processar a imagem: {str(ex)}")
            return None
            
        finally:
            # Always release .NET lock if it was acquired
            if lock_acquired and hasattr(image, "ExitLock"):
                try:
                    image.ExitLock()
                except Exception as ex:
                    self.logger.error(f"Error releasing image lock: {str(ex)}")


    def convert_temperature_unit(
        self, temperature, unit_from="Kelvin", unit_to="Celsius"
    ):
        """
        Convert the temperature from one unit to another.

        Args:
            temperature: The temperature to convert.
            unit_from: The unit to convert from.
            unit_to: The unit to convert to.

        Returns:
            The converted temperature.
        """
        if unit_from == unit_to:
            return temperature

        # Convert from the source unit to Kelvin
        if unit_from == "Celsius":
            temperature_in_kelvin = temperature + 273.15
        elif unit_from == "Fahrenheit":
            temperature_in_kelvin = (temperature - 32) * 5 / 9 + 273.15
        elif unit_from == "Kelvin":
            temperature_in_kelvin = temperature
        else:
            raise ValueError(f"Unsupported temperature unit: {unit_from}")

        # Convert from Kelvin to the target unit
        if unit_to == "Celsius":
            return temperature_in_kelvin - 273.15
        elif unit_to == "Fahrenheit":
            return (temperature_in_kelvin - 273.15) * 9 / 5 + 32
        elif unit_to == "Kelvin":
            return temperature_in_kelvin
        else:
            raise ValueError(f"Unsupported temperature unit: {unit_to}")
