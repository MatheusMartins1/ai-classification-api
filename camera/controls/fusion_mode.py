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


class CameraControlFusionMode:
    def __init__(self, _camera):
        self._camera = _camera
        self.logger = _camera.logger

        self.is_fusion_mode_supported = None
        self.fusion = None

    def get_fusion_mode(self) -> None | live.Remote.FusionMode:
        """
        Get the current fusion mode.

        Returns:
            FusionMode: The current fusion mode.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            return self._camera.RemoteControl.FusionSettings.GetFusionMode()
        except Exception as e:
            self.logger.error(f"Error getting fusion mode: {e}")
            return None

    def is_fusion_supported(self) -> None | bool:
        """
        Check if fusion is supported.

        Returns:
            bool: True if fusion is supported.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            return self._camera.RemoteControl.FusionSettings.IsFusionSupported()
        except Exception as e:
            self.logger.error(f"Error checking if fusion is supported: {e}")
            return None

    def set_fusion_mode(self, mode: str) -> None:
        """
        Set the fusion mode.

        Args:
            mode (FusionMode): The fusion mode to set.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        modes = {
            "ThermalOnly": live.Remote.FusionMode.ThermalOnly,
            "PictureInPicture": live.Remote.FusionMode.PictureInPicture,
            "Msx": live.Remote.FusionMode.Msx,
            "VisualOnly": live.Remote.FusionMode.VisualOnly,
        }

        selected_mode = modes.get(mode)

        if not selected_mode:
            self.logger.error(f"Invalid fusion mode: {mode}")
            return None

        try:
            self._camera.RemoteControl.FusionSettings.SetFusionMode(selected_mode)
        except Exception as e:
            self.logger.error(f"Error setting fusion mode: {e}")
            return None
