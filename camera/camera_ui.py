"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

import os

import clr

from config.settings import settings

# Add the path to the directory containing the compiled DLL
dll_path = os.path.join(settings.BASE_DIR, "ThermalCameraLibrary")

clr.AddReference(os.path.join(dll_path, "ThermalCamera.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Live.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Image.dll"))
clr.AddReference("System")
# clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Gigevision.dll"))

import time
from datetime import datetime

import Flir.Atlas.Image as Image  # type: ignore

# Import the necessary classes from the assembly
import Flir.Atlas.Live as live  # type: ignore


# TODO: Implement the CameraUIManager class
class CameraUIManager:
    def __init__(self, _camera):
        self._camera = _camera

        self.fps = 0
        self.fps_load_data = 0.0
        self.frame_counter_fps = 0
        self.frame_counter = 0
        self.skip_frames = 1
        self.lost_images = 0
        self.label_cam_info_size = None
        self.label_cam_info_ip = None
        self.label_cam_info_name = None
        self.stopwatch_fps = time.time()
        self.elapsed_time = time.time()
        self.elapsed_time_start = None
        self.elapsed_time_end = None
        self.overlay = None

        # TODO: Implementar informações do sistema
        self.cpu_usage = "0%"
        self.memory_usage = "0 MB"
        self.running_time = "0:00:00"
        self.camera_info = "N/A"

    def update_camera_information(self, image):
        """
        Update the camera information based on the received image.

        Args:
            image: The received image.
        """
        # FIXME: Verificar se a imagem é válida

        self._camera.camera_control.camera_control_settings.update_settings()
        self._camera.measurements_handler.update_settings()

        try:
            self.label_cam_info_size = f"{self._camera.image_obj_thermal.Width} x {self._camera.image_obj_thermal.Height}"
            self.fps = f"{self._camera.camera.Fps:.3f}"
            self.frame_counter = f"{self._camera.camera.FrameCount}"
            self.lost_images = f"{self._camera.camera.LostImages}"
            if self._camera.camera.CameraDeviceInfo.IpSettings is not None:
                self.label_cam_info_ip = (
                    self._camera.camera.CameraDeviceInfo.IpSettings.IpAddress
                )
            else:
                self.label_cam_info_ip = "N/A"
            self.label_cam_info_name = self._camera.camera.CameraDeviceInfo.Name
        except Exception as ex:
            self.logger.error(str(ex))

    def start_elapsed_time(self):
        """
        Start the elapsed time counter.
        """
        self.elapsed_time_start = time.perf_counter()
        self.elapsed_time_end = None

    def stop_elapsed_time(self):
        """
        Stop the elapsed time counter.
        """
        if self.elapsed_time_start is not None:
            self.elapsed_time_end = time.perf_counter()

    def get_elapsed_time(self):
        """
        Get the elapsed time in seconds.

        Returns:
            The elapsed time in seconds, or None if the timer has not been started.
        """
        if self.elapsed_time_start is not None:
            if self.elapsed_time_end is not None:
                return self.elapsed_time_end - self.elapsed_time_start
            else:
                return time.perf_counter() - self.elapsed_time_start
        return None
