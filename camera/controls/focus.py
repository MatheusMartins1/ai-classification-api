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

# Import the necessary classes from the assembly
import Flir.Atlas.Live as live  # type: ignore


class CameraControlFocus:
    def __init__(self, _camera):
        self._camera = _camera
        self.logger = _camera.logger

        self.is_continuous_focus_enabled = None
        self.is_focus_supported = None

        self.distance = None
        self.auto_focus_roi = None
        self.speed = None

    def set_focus_mode(self, mode):
        """
        Set the camera focus mode based on the provided mode.

        Args:
            mode (str): The focus mode to set. Valid values are 'near', 'stop', 'far', 'auto'.

        Concerns
            Async
        """
        # TEST: Asynchronous function call

        if self._camera:
            focus_modes = {
                "near": live.Remote.FocusMode.Near,
                "stop": live.Remote.FocusMode.Stop,
                "far": live.Remote.FocusMode.Far,
                "auto": live.Remote.FocusMode.Auto,
            }
            if mode in focus_modes:
                try:
                    self._camera.camera.RemoteControl.Focus.Mode(focus_modes[mode])

                except Exception as e:
                    self.logger.error(f"Error setting focus mode: {e}")
            else:
                self.logger.error(f"Invalid focus mode: {mode}")

    def disable_continuous_focus(self) -> None:
        """
        Disable continuous focus.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            self._camera.camera.RemoteControl.Focus.DisableContinuousFocus()
        except Exception as e:
            self.logger.error(f"Error disabling continuous focus: {e}")
            return None

    def enable_continuous_focus(self) -> None:
        """
        Enable continuous focus.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            self._camera.camera.RemoteControl.Focus.EnableContinuousFocus()
        except Exception as e:
            self.logger.error(f"Error enabling continuous focus: {e}")
            return None

    def get_distance(self) -> None | float:
        """
        Get focus distance in meters.

        Returns:
            float: Distance in meters.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            return self._camera.camera.RemoteControl.Focus.GetDistance()
        except Exception as e:
            self.logger.error(f"Error getting focus distance: {e}")
            return None

    def get_autofocus_roi(self) -> None | str:
        """
        Get auto focus region of interest.

        Returns:
            Rectangle: The region of interest.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """

        # TEST: if the parameter is a Rectangle
        # roi: Rectangle

        try:
            return self._camera.camera.RemoteControl.Focus.GetRoi()
        except Exception as e:
            self.logger.error(f"Error getting region of interest: {e}")
            return None

    def get_speed(self) -> None | int:
        """
        Get focus speed.

        Returns:
            int: Focus engine speed. Range -100 to 100.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            return self._camera.camera.RemoteControl.Focus.GetSpeed()
        except Exception as e:
            self.logger.error(f"Error getting focus speed: {e}")
            return None

    def get_is_continuous_focus_enabled(self) -> None | bool:
        """
        Check if continuous focus is enabled.

        Returns:
            bool: True if continuous focus is enabled.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            return self._camera.camera.RemoteControl.Focus.IsContinuousFocusEnabled()
        except Exception as e:
            self.logger.error(f"Error checking if continuous focus is enabled: {e}")
            return None

    def get_is_focus_supported(self) -> None | bool:
        """
        Check if the camera supports focus.

        Returns:
            bool: True if focus is supported.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            return self._camera.camera.RemoteControl.Focus.IsSupported()
        except Exception as e:
            self.logger.error(f"Error checking if focus is supported: {e}")
            return None

    def set_distance(self, distance: float) -> None:
        """
        Set focus distance in meters.

        Args:
            distance (float): Distance in meters.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            self._camera.camera.RemoteControl.Focus.SetDistance(distance)
        except Exception as e:
            self.logger.error(f"Error setting focus distance: {e}")
            return None

    def set_autofocus_roi(self, roi: str) -> None:
        """
        Set auto focus region of interest.

        Args:
            roi (Rectangle): Region of interest.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """

        # TEST: if the parameter is a Rectangle
        # roi: Rectangle

        try:
            self._camera.camera.RemoteControl.Focus.SetRoi(roi)
        except Exception as e:
            self.logger.error(f"Error setting region of interest: {e}")
            return None

    def set_speed(self, speed: int) -> None:
        """
        Set focus speed.

        Args:
            speed (int): Focus engine speed. Range -100 to 100.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            self._camera.camera.RemoteControl.Focus.SetSpeed(speed)
        except Exception as e:
            self.logger.error(f"Error setting focus speed: {e}")
            return None
