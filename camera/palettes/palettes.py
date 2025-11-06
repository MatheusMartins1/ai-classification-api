"""
Developer: Matheus Martins da Silva
Creation Date: 07/2025
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

import os
from threading import Lock
from typing import Any, Dict, List, Optional

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

from utils import object_handler


class PaletteHandler:
    """
    PaletteHandler provides methods to handle palettes from Flir cameras.

    Based on Flir Atlas SDK 7.5.0 documentation:
    - PaletteManager: https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/class_flir_1_1_atlas_1_1_image_1_1_palettes_1_1_palette_manager.html
    - Palette: https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/class_flir_1_1_atlas_1_1_image_1_1_palettes_1_1_palette.html#details
    """

    def __init__(self, _camera):
        """
        Initialize the PaletteHandler class with a camera instance.

        Args:
            _camera: Camera instance with thermal image
        """
        self._camera = _camera
        self.logger = _camera.logger
        self._service_lock = _camera.service_lock

        self._thermal_image = _camera.image_obj_thermal
        self._visual_image = _camera.image_obj_visual
        self.is_supported = True

        # Initialize palette objects
        self._palette_manager = None
        self._current_palette = None
        self._supported_palettes = []

        # Current Palette properties
        self.name = None
        self.palette_version = None
        self.underflow_color = None
        self.overflow_color = None
        self.below_span_color = None
        self.above_span_color = None
        self.is_inverted = None
        self.palette_colors = []

        # Built-in palette names from SDK
        self.built_in_palette_names = [
            "Arctic",
            "Cool",
            "Grey",
            "Iron",
            "Lava",
            "Rainbow",
            "RainHighContrast",
            "Warm",
        ]
        self.available_palettes = []
        self.current_palette = None

        self.update_info()

    def _check_if_supported(self, thermal_image: Optional[Any] = None):
        """
        Check if the palette information is supported by the camera.
        """
        if thermal_image is None and self._thermal_image is None:
            self.is_supported = False
            return

        try:
            if thermal_image.PaletteManager is None:
                self.is_supported = False
                return
        except Exception as e:
            self.is_supported = False
            return

    def update_info(self, thermal_image: Optional[Any] = None) -> None:
        """
        Update the palette information from the thermal image.

        Args:
            thermal_image: Optional thermal image object
        """
        with self._service_lock:
            if thermal_image is None and self._thermal_image is None:
                return

            thermal_image = (
                thermal_image
                if isinstance(thermal_image, Image.ThermalImage)
                else self._thermal_image
            )

            # Update PaletteManager info
            self._palette_manager = thermal_image.PaletteManager
            self._check_if_supported(thermal_image)

            self._supported_palettes = self._get_supported_palettes(thermal_image)

            # Update current Palette info
            self._update_current_palette_info(thermal_image)

            self.available_palettes = [
                {k: v for k, v in p.items() if k not in ["colors", "palette"]}
                for p in self._supported_palettes
            ]

    def _get_supported_palettes(self, thermal_image: Any) -> List[Dict[str, Any]]:
        """
        Get list of supported palette information as dictionaries.

        Returns:
            List[Dict[str, Any]]: List of palette dictionaries with index, name, palette object, and colors
        """
        palettes = []
        try:
            if thermal_image.PaletteManager and thermal_image.PaletteManager.Palettes:
                palettes_enum = thermal_image.PaletteManager.Palettes.GetEnumerator()
                palette_count = thermal_image.PaletteManager.Palettes.Count

                if palettes_enum and palette_count > 0:
                    index = 0
                    while palettes_enum.MoveNext():
                        current_palette = palettes_enum.Current

                        colors = []
                        colors_enum = current_palette.PaletteColors.GetEnumerator()
                        colors_count = current_palette.PaletteColors.Count

                        if colors_enum and colors_count > 0:
                            index_colors = 0
                            while colors_enum.MoveNext():
                                current_color = colors_enum.Current
                                color_dict = self._extract_color_properties(
                                    color_object=current_color
                                )
                                if color_dict:
                                    colors.append(
                                        {
                                            "index": index_colors,
                                            "color_dict": color_dict,
                                            "color": current_color,
                                        }
                                    )
                                index_colors += 1
                        else:
                            self.logger.debug(
                                "No colors available or enumerator is empty"
                            )

                        if hasattr(current_palette, "Name"):
                            palette_name = current_palette.Name
                            palettes.append(
                                {
                                    "index": index,
                                    "name": palette_name,
                                    "palette": current_palette,
                                    "colors": colors,
                                }
                            )
                        index += 1

                    # self.logger.info(f"Found {len(palettes)} supported palettes")
                else:
                    self.logger.debug("No palettes available or enumerator is empty")
            else:
                self.logger.debug("PaletteManager or Palettes not available")

        except Exception as e:
            self.logger.error(f"Error getting supported palettes: {e}")

        return palettes

    def _update_current_palette_info(self, thermal_image: Any) -> None:
        """
        Update current Palette information.

        Args:
            thermal_image: Thermal image object
        """
        try:
            if thermal_image.Palette is None:
                self.logger.warning("Current Palette not available")
                return

            self._current_palette = thermal_image.Palette

            # Extract palette properties
            self.name = object_handler.safe_extract_attribute(
                self._current_palette, "Name", convert_type="str"
            )

            self.palette_version = object_handler.safe_extract_attribute(
                self._current_palette, "Version", convert_type="str"
            )

            # Extract color properties with A, R, G, B values
            self.underflow_color = self._extract_color_properties(
                palette_object=self._current_palette,
                color_property_name="UnderflowColor",
            )

            self.overflow_color = self._extract_color_properties(
                palette_object=self._current_palette,
                color_property_name="OverflowColor",
            )

            self.below_span_color = self._extract_color_properties(
                palette_object=self._current_palette,
                color_property_name="BelowSpanColor",
            )

            self.above_span_color = self._extract_color_properties(
                palette_object=self._current_palette,
                color_property_name="AboveSpanColor",
            )

            self.is_inverted = object_handler.safe_extract_attribute(
                self._current_palette, "IsInverted", convert_type="bool"
            )

            # Get palette colors
            try:
                if hasattr(self._current_palette, "PaletteColors"):
                    colors = self._current_palette.PaletteColors
                    self.palette_colors = list(colors) if colors else []
                else:
                    self.palette_colors = []
            except Exception as e:
                self.logger.warning(f"Error getting palette colors: {e}")
                self.palette_colors = []

        except Exception as e:
            self.logger.error(f"Error updating current palette info: {e}")

    def _extract_color_properties(
        self,
        palette_object: Optional[Any] = None,
        color_property_name: Optional[str] = None,
        color_object: Optional[Any] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Extract A, R, G, B properties from a System.Drawing.Color object.

        Args:
            palette_object: The palette object containing the color property
            color_property_name: Name of the color property to extract

        Returns:
            Dictionary with A, R, G, B values or None if extraction fails
        """
        try:
            if color_object is not None:
                color_object = color_object
            elif palette_object is not None and color_property_name is not None:
                color_object = getattr(palette_object, color_property_name)
            else:
                return None

            if color_object is None:
                return None

            # Extract A, R, G, B properties from System.Drawing.Color
            alpha = getattr(color_object, "A", None)
            red = getattr(color_object, "R", None)
            green = getattr(color_object, "G", None)
            blue = getattr(color_object, "B", None)

            # Check if all properties were extracted successfully
            if all(val is not None for val in [alpha, red, green, blue]):
                color_dict = {
                    "name": color_object.Name,
                    "is_empty": color_object.IsEmpty,
                    "is_known_color": color_object.IsKnownColor,
                    "is_named_color": color_object.IsNamedColor,
                    "is_system_color": color_object.IsSystemColor,
                    "color": {
                        "A": (
                            int(alpha) if alpha is not None else 0
                        ),  # Alpha (transparency) - 0-255
                        "R": int(red) if red is not None else 0,  # Red - 0-255
                        "G": int(green) if green is not None else 0,  # Green - 0-255
                        "B": int(blue) if blue is not None else 0,  # Blue - 0-255
                    },
                }
                return color_dict
            else:
                self.logger.warning(
                    f"Failed to extract complete color properties for {color_property_name}"
                )
                return None

        except Exception as e:
            self.logger.warning(
                f"Error extracting color properties for {color_property_name}: {e}"
            )
            return None

    def set_palette(self, palette_name: str) -> bool:
        """
        Set the current palette by name using the palette object from _supported_palettes.

        Args:
            palette_name: Name of the palette to set

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self._service_lock:
                # Find the palette in _supported_palettes
                target_palette = None
                for palette_info in self._supported_palettes:
                    if palette_info.get("name") == palette_name:
                        target_palette = palette_info.get("palette")
                        break

                if target_palette:
                    self._thermal_image.Palette = target_palette
                    self.update_info()
                    self.logger.info(f"Palette set to: {palette_name}")
                    return True
                else:
                    self.logger.warning(
                        f"Palette '{palette_name}' not found in supported palettes"
                    )
                    return False

        except Exception as e:
            self.logger.error(f"Error setting palette '{palette_name}': {e}")
            return False

    def set_palette_by_name(self, palette_name: str) -> bool:
        """
        Set the current palette by name using PaletteManager.FromString.

        Args:
            palette_name: Name of the palette to set

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self._service_lock:
                if self._palette_manager and hasattr(
                    self._palette_manager, "FromString"
                ):
                    # Use the static method FromString
                    new_palette = self._palette_manager.FromString(palette_name)
                    if new_palette:
                        self._thermal_image.Palette = new_palette
                        self.update_info()
                        self.logger.info(f"Palette set to: {palette_name}")
                        return True
                    else:
                        self.logger.warning(f"Palette '{palette_name}' not found")
                        return False
                else:
                    self.logger.warning("PaletteManager.FromString not available")
                    return False
        except Exception as e:
            self.logger.error(f"Error setting palette by name '{palette_name}': {e}")
            return False

    def set_built_in_palette(self, palette_name: str) -> bool:
        """
        Set a built-in palette by name using the palette object from _supported_palettes.

        Args:
            palette_name: Name of the built-in palette (Arctic, Cool, Grey, etc.)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self._service_lock:
                # Find the palette in _supported_palettes
                target_palette = None
                for palette_info in self._supported_palettes:
                    if palette_info.get("name") == palette_name:
                        target_palette = palette_info.get("palette")
                        break

                if target_palette:
                    self._thermal_image.Palette = target_palette
                    self.update_info()
                    self.logger.info(f"Built-in palette set to: {palette_name}")
                    return True
                else:
                    self.logger.warning(
                        f"Built-in palette '{palette_name}' not found in supported palettes"
                    )
                    return False

        except Exception as e:
            self.logger.error(f"Error setting built-in palette '{palette_name}': {e}")
            return False

    def set_built_in_palette_by_name(self, palette_name: str) -> bool:
        """
        Set a built-in palette by name from the available built-in palettes.

        Args:
            palette_name: Name of the built-in palette to set

        Returns:
            bool: True if successful, False otherwise
        """
        # Check if the palette name is in the list of available built-in palettes
        if palette_name not in self.built_in_palette_names:
            self.logger.warning(f"Invalid built-in palette name: {palette_name}")
            self.logger.info(
                f"Available built-in palettes: {', '.join(self.built_in_palette_names)}"
            )
            return False
        # Use the existing set_built_in_palette method
        return self.set_built_in_palette(palette_name)

    # TEST: TEST IMPORT FROM A .pal
    def load_palette_from_file(self, file_path: str) -> bool:
        """
        Load a palette from a .pal file using PaletteManager.Open.

        Args:
            file_path: Path to the .pal file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self._service_lock:
                if self._palette_manager and hasattr(self._palette_manager, "Open"):
                    # Use the static method Open
                    new_palette = self._palette_manager.Open(file_path)
                    if new_palette:
                        self._thermal_image.Palette = new_palette
                        self.update_info()
                        self.logger.info(f"Palette loaded from file: {file_path}")
                        return True
                    else:
                        self.logger.warning(
                            f"Failed to load palette from file: {file_path}"
                        )
                        return False
                else:
                    self.logger.warning("PaletteManager.Open not available")
                    return False
        except Exception as e:
            self.logger.error(f"Error loading palette from file '{file_path}': {e}")
            return False

    def set_palette_inverted(self, inverted: bool) -> bool:
        """
        Set whether the palette is inverted.

        Args:
            inverted: True to invert colors, False otherwise

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self._service_lock:
                if self._current_palette and hasattr(
                    self._current_palette, "IsInverted"
                ):
                    self._current_palette.IsInverted = bool(inverted)
                    self.update_info()
                    self.logger.info(f"Palette inverted set to: {inverted}")
                    return True
                else:
                    self.logger.warning(
                        "Current palette or IsInverted property not available"
                    )
                    return False
        except Exception as e:
            self.logger.error(f"Error setting palette inverted: {e}")
            return False

    def reset_to_default_palette(self) -> bool:
        """
        Reset to the default palette using PaletteManager.FromImage.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self._service_lock:
                if self._palette_manager and hasattr(
                    self._palette_manager, "FromImage"
                ):

                    default_palette = self._palette_manager.FromImage
                    if default_palette:
                        self._thermal_image.Palette = default_palette
                        self.update_info()
                        self.logger.info("Reset to default palette (FromImage)")
                        return True
                    else:
                        self.logger.warning("Default palette (FromImage) not available")
                        return False
                else:
                    self.logger.warning("PaletteManager.FromImage not available")
                    return False
        except Exception as e:
            self.logger.error(f"Error resetting to default palette: {e}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert palette information to dictionary format.

        Returns:
            Dictionary containing all palette information
        """
        return {
            "available_palettes": self.available_palettes,
            "current_palette": {
                "name": self.name,
                "is_inverted": self.is_inverted,
                "underflow_color": self.underflow_color,
                "overflow_color": self.overflow_color,
                "below_span_color": self.below_span_color,
                "above_span_color": self.above_span_color,
                "version": self.palette_version,
            },
        }

    def to_string(self) -> Dict[str, Any]:
        """
        Alias for to_dict() to maintain consistency with other resource classes.

        Returns:
            Dictionary containing all palette information
        """
        return self.to_dict()
