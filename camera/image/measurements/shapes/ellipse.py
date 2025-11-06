"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

import os
from typing import Iterator, List, Optional

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


class MeasurementEllipseManager:
    """
    Holds the measurement ellipse functionality.
    """

    def __init__(self, _camera):
        """
        Initialize the MeasurementEllipseManager class with a camera instance.
        """
        self._camera = self._camera
        self._logger = _camera._logger
        self._image = _camera.image_obj_thermal
        self._visual_image = _camera.image_obj_visual
