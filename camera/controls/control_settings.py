"""
Developer: Matheus Martins da Silva
Creation Date: 2024-12-19
Description: Camera control settings management for Flir Atlas SDK integration.
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva.
"""

import os
from typing import List, Optional

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

DistanceUnit = Image.DistanceUnit
TemperatureUnit = Image.TemperatureUnit
Range = Image.Range

ScaleAdjustMode = live.Remote.ScaleAdjustMode
VideoMode = live.Remote.VideoMode


class CameraControlSettings:
    """
    A class to manage the camera control settings.

    Reference:
    https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/class_flir_1_1_atlas_1_1_live_1_1_remote_1_1_remote_camera_settings.html
    """

    def __init__(self, _camera):
        """
        Initialize the camera control settings.

        Args:
            _camera: The camera manager instance.
        """
        self._camera = _camera
        self.logger = _camera.logger

        # Initialize settings attributes
        self.atmospheric_temperature = None
        self.distance_unit = None
        self.external_optics_temperature = None
        self.external_optics_transmission = None
        self.ext_opt_trans_alt_val = None
        self.is_ext_opt_transm_alt_active = None
        self.is_scale_adjust_enabled = None
        self.object_distance = None
        self.object_emissivity = None
        self.palette_name = None
        self.reference_temperature = None
        self.reflected_temperature = None
        self.relative_humidity = None
        self.scale_adjust_mode = None
        self.scale_limits = None
        self.send_lens_temp = None
        self.temperature_range_index = None
        self.temperature_unit = None
        self.time_until_camera_is_ready = None
        self.t_lens_ext = None
        self.video_mode = None
        self.zoom_factor = None

        self.is_battery_charging = None
        self.is_high_sensitivity_mode_enabled = None
        self.is_high_sensitivity_mode_supported = None
        self.is_shutter_enabled = None
        self.is_shutter_supported = None

    def _check_camera_ready(self) -> bool:
        """
        Check if the camera is ready for RemoteControl operations.

        Returns:
            bool: True if the camera is ready, False otherwise.
        """
        try:
            # Check if camera is connected
            if not self._camera.camera or not self._camera.camera.IsConnected:
                self.logger.warning("Camera not connected")
                return False

            # Check if RemoteControl is available
            if (
                not hasattr(self._camera.camera, "RemoteControl")
                or not self._camera.camera.RemoteControl
            ):
                self.logger.warning("RemoteControl not available")
                return False

            # Check if CameraSettings is available
            if (
                not hasattr(self._camera.camera.RemoteControl, "CameraSettings")
                or not self._camera.camera.RemoteControl.CameraSettings
            ):
                self.logger.warning("CameraSettings not available")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error checking camera readiness: {e}")
            return False

    def update_settings(self):
        """
        Initialize all settings by calling the respective get methods.
        """
        self.atmospheric_temperature = self.get_atmospheric_temperature()
        self.distance_unit = self.get_distance_unit()
        self.external_optics_temperature = self.get_external_optics_temperature()
        self.external_optics_transmission = self.get_external_optics_transmission()
        self.ext_opt_trans_alt_val = self.get_ext_opt_trans_alt_val()
        self.is_ext_opt_transm_alt_active = self.get_is_ext_opt_transm_alt_active()
        self.is_scale_adjust_enabled = self.get_is_scale_adjust_enabled()
        self.object_distance = self.get_object_distance()
        self.object_emissivity = self.get_object_emissivity()
        self.palette_name = self.get_palette_name()
        self.reference_temperature = self.get_reference_temperature()
        self.reflected_temperature = self.get_reflected_temperature()
        self.relative_humidity = self.get_relative_humidity()
        self.scale_adjust_mode = self.get_scale_adjust_mode()
        self.scale_limits = self.get_scale_limits()
        self.send_lens_temp = self.get_send_lens_temp()
        self.temperature_range_index = self.get_temperature_range_index()
        self.temperature_unit = self.get_temperature_unit()
        self.time_until_camera_is_ready = self.get_time_until_camera_is_ready()
        self.t_lens_ext = self.get_t_lens_ext()
        self.video_mode = self.get_video_mode()
        self.zoom_factor = self.get_zoom_factor()

        self.is_battery_charging = self.get_is_battery_charging()
        self.is_high_sensitivity_mode_enabled = (
            self.get_is_high_sensitivity_mode_enabled()
        )
        self.is_high_sensitivity_mode_supported = (
            self.get_is_high_sensitivity_mode_supported()
        )
        self.is_shutter_enabled = self.get_is_shutter_enabled()
        self.is_shutter_supported = self.get_is_shutter_supported()

    def EnumerateTemperatureRanges(self) -> Optional[List[Image.Range]]:
        """
        Array of temperature ranges (in Kelvin). Use this method to determine the number of available temperature ranges.
        Use the array index to modify the temperature range SetTemperatureRangeIndex.

        Returns:
            Optional[List[Range]]: Array of temperature ranges.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
            ArgumentException: If the argument is invalid.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                ranges = (
                    self._camera.camera.RemoteControl.CameraSettings.EnumerateTemperatureRanges()
                )
                return [Range(r.Minimum, r.Maximum) for r in ranges]
        except Exception as e:
            self.logger.error(f"Error enumerating temperature ranges: {e}")
            return None

    def get_atmospheric_temperature(self) -> Optional[float]:
        """
        Get the atmospheric temperature from the camera.

        Returns:
            Optional[float]: Atmospheric temperature in Kelvin. Range 0 - 5000.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                temp = (
                    self._camera.camera.RemoteControl.CameraSettings.GetAtmosphericTemperature()
                )
                return temp
        except Exception as e:
            self.logger.error(f"Error getting atmospheric temperature: {e}")
            return None

    def get_external_optics_temperature(self) -> Optional[float]:
        """
        Get the external optics temperature from the camera.

        Returns:
            Optional[float]: External optics temperature in Kelvin. Range 0 - 5000.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return (
                    self._camera.camera.RemoteControl.CameraSettings.GetExternalOpticsTemperature()
                )
        except Exception as e:
            self.logger.error(f"Error getting external optics temperature: {e}")
            return None

    def get_external_optics_transmission(self) -> Optional[float]:
        """
        Get the external optics transmission from the camera.

        Returns:
            Optional[float]: External optics transmission in percentage. Range 0.1 - 100.0%.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return (
                    self._camera.camera.RemoteControl.CameraSettings.GetExternalOpticsTransmission()
                )
        except Exception as e:
            self.logger.error(f"Error getting external optics transmission: {e}")
            return None

    def get_ext_opt_trans_alt_val(self) -> Optional[float]:
        """
        Get the external optics (window) transmission.

        This method retrieves the transmission value for external optics/window.
        Not all camera models support this feature.

        Returns:
            Optional[float]: The external optics transmission (0.1 to 1.0), or None if not supported.
        """
        with self._camera._locks("control"):
            try:
                if not self._check_camera_ready():
                    return None

                # Check if the camera supports external optics transmission
                if not hasattr(
                    self._camera.camera.RemoteControl.CameraSettings,
                    "GetExtOptTransmAltVal",
                ):
                    self.logger.warning(
                        "Camera does not support external optics transmission"
                    )
                    return None

                ExtOptTransmAltVal = (
                    self._camera.camera.RemoteControl.CameraSettings.GetExtOptTransmAltVal()
                )
                return ExtOptTransmAltVal
            except Exception as e:
                self.logger.warning(
                    f"External optics transmission not supported or failed: {e}"
                )
                return None

    def get_is_ext_opt_transm_alt_active(self) -> Optional[bool]:
        """
        Check if external optics (window) is activated.

        This method checks if external optics/window transmission is active.
        Not all camera models support this feature.

        Returns:
            Optional[bool]: True if active, None if not supported.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                # Check if the camera supports this feature
                if not hasattr(
                    self._camera.camera.RemoteControl.CameraSettings,
                    "GetIsExtOptTransmAltActive",
                ):
                    self.logger.warning(
                        "Camera does not support external optics transmission check"
                    )
                    return None

                return (
                    self._camera.camera.RemoteControl.CameraSettings.GetIsExtOptTransmAltActive()
                )
        except Exception as e:
            self.logger.warning(
                f"External optics transmission check not supported or failed: {e}"
            )
            return None

    def get_is_scale_adjust_enabled(self) -> Optional[bool]:
        """
        Get if the scale adjust is active.

        Returns:
            Optional[bool]: True if active.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return (
                    self._camera.camera.RemoteControl.CameraSettings.GetIsScaleAdjustEnabled()
                )
        except Exception as e:
            self.logger.error(f"Error checking scale adjust enabled: {e}")
            return None

    def get_object_distance(self) -> Optional[float]:
        """
        Get the object distance from the camera.

        Returns:
            Optional[float]: Object distance in meters. Range 0 - 10000.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return (
                    self._camera.camera.RemoteControl.CameraSettings.GetObjectDistance()
                )
        except Exception as e:
            self.logger.error(f"Error getting object distance: {e}")
            return None

    def get_object_emissivity(self) -> Optional[float]:
        """
        Get the object emissivity from the camera.

        Returns:
            Optional[float]: Object emissivity. Range 0.01 - 1.00.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return (
                    self._camera.camera.RemoteControl.CameraSettings.GetObjectEmissivity()
                )
        except Exception as e:
            self.logger.error(f"Error getting object emissivity: {e}")
            return None

    def get_palette_name(self) -> Optional[str]:
        """
        Get the current palette name from the camera.

        Returns:
            Optional[str]: The palette name.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return self._camera.camera.RemoteControl.CameraSettings.GetPaletteName()
        except Exception as e:
            self.logger.error(f"Error getting palette name: {e}")
            return None

    def get_reference_temperature(self) -> Optional[float]:
        """
        Get the reference temperature from the camera.

        Returns:
            Optional[float]: Reference temperature in Kelvin. Range 0 - 5000.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return (
                    self._camera.camera.RemoteControl.CameraSettings.GetReferenceTemperature()
                )
        except Exception as e:
            self.logger.error(f"Error getting reference temperature: {e}")
            return None

    def get_reflected_temperature(self) -> Optional[float]:
        """
        Get the reflected temperature from the camera.

        Returns:
            Optional[float]: Reflected temperature in Kelvin. Range 0 - 5000.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return (
                    self._camera.camera.RemoteControl.CameraSettings.GetReflectedTemperature()
                )
        except Exception as e:
            self.logger.error(f"Error getting reflected temperature: {e}")
            return None

    def get_relative_humidity(self) -> Optional[float]:
        """
        Get the relative humidity from the camera.

        Returns:
            Optional[float]: Relative humidity in percentage. Range 0 - 100%.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return (
                    self._camera.camera.RemoteControl.CameraSettings.GetRelativeHumidity()
                )
        except Exception as e:
            self.logger.error(f"Error getting relative humidity: {e}")
            return None

    def get_send_lens_temp(self) -> Optional[bool]:
        """
        Check if a virtual temperature sensor is active.

        Returns:
            Optional[bool]: True if virtual sensor is activated.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return (
                    self._camera.camera.RemoteControl.CameraSettings.GetSendLensTemp()
                )
        except Exception as e:
            self.logger.error(f"Error checking send lens temp: {e}")
            return None

    def get_temperature_range_index(self) -> Optional[int]:
        """
        Get the current selected temperature range index.

        Returns:
            Optional[int]: Zero based index.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return (
                    self._camera.camera.RemoteControl.CameraSettings.GetTemperatureRangeIndex()
                )
        except Exception as e:
            self.logger.error(f"Error getting temperature range index: {e}")
            return None

    def get_time_until_camera_is_ready(self) -> Optional[int]:
        """
        Get the time in seconds until the camera is cooled down.

        Returns:
            Optional[int]: Time in seconds until the camera is cooled down.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return (
                    self._camera.camera.RemoteControl.CameraSettings.GetTimeUntilCameraIsReady()
                )
        except Exception as e:
            self.logger.error(f"Error getting time until camera is ready: {e}")
            return None

    def get_t_lens_ext(self) -> Optional[float]:
        """
        Get the external temperature sensor (gets the external optics/window temperature).

        Returns:
            Optional[float]: The external temperature.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return self._camera.camera.RemoteControl.CameraSettings.GetTLensExt()
        except Exception as e:
            self.logger.error(f"Error getting T lens ext: {e}")
            return None

    def get_zoom_factor(self) -> Optional[float]:
        """
        Get the zoom factor from the camera.

        Returns:
            Optional[float]: Zoom factor.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return self._camera.camera.RemoteControl.CameraSettings.GetZoomFactor()
        except Exception as e:
            self.logger.error(f"Error getting zoom factor: {e}")
            return None

    """ Enum functions """

    def get_distance_unit(self) -> Optional[DistanceUnit]:
        """
        Get the distance unit used in the camera.

        Returns:
            Optional[DistanceUnit]: The distance unit used in the camera, or None if an error occurs.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return (
                    self._camera.camera.RemoteControl.CameraSettings.GetDistanceUnit()
                )
        except Exception as e:
            self.logger.error(f"Error getting distance unit: {e}")
            return None

    def get_video_mode(self) -> Optional[VideoMode]:
        """
        Get the camera video mode (PAL or NTSC).

        Returns:
            Optional[VideoMode]: The current video mode.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return self._camera.camera.RemoteControl.CameraSettings.GetVideoMode()
        except Exception as e:
            self.logger.error(f"Error getting video mode: {e}")
            return None

    def get_scale_adjust_mode(self) -> Optional[ScaleAdjustMode]:
        """
        Get the scale adjust mode from the camera.

        Returns:
            Optional[ScaleAdjustMode]: The scale adjust mode.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return (
                    self._camera.camera.RemoteControl.CameraSettings.GetScaleAdjustMode()
                )
        except Exception as e:
            self.logger.error(f"Error getting scale adjust mode: {e}")
            return None

    def get_scale_limits(self) -> Optional[Range]:
        """
        Get the scale range from the camera.

        Returns:
            Optional[Range]: The scale limits.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return self._camera.camera.RemoteControl.CameraSettings.GetScaleLimits()
        except Exception as e:
            self.logger.error(f"Error getting scale limits: {e}")
            return None

    def get_temperature_unit(self) -> Optional[TemperatureUnit]:
        """
        Get the used temperature unit from the camera.

        Returns:
            Optional[TemperatureUnit]: The temperature unit.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return (
                    self._camera.camera.RemoteControl.CameraSettings.GetTemperatureUnit()
                )
        except Exception as e:
            self.logger.error(f"Error getting temperature unit: {e}")
            return None

    def get_is_battery_charging(self) -> Optional[bool]:
        """
        Check if the camera battery is charging.

        Returns:
            Optional[bool]: True if charging.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return (
                    self._camera.camera.RemoteControl.CameraSettings.IsBatteryCharging()
                )
        except Exception as e:
            self.logger.error(f"Error checking battery charging: {e}")
            return None

    def get_is_high_sensitivity_mode_enabled(self) -> Optional[bool]:
        """
        Check if High Sensitivity Mode is enabled.

        Returns:
            Optional[bool]: True if HSM is enabled.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return (
                    self._camera.camera.RemoteControl.CameraSettings.IsHighSensitivityModeEnabled()
                )
        except Exception as e:
            self.logger.error(f"Error checking high sensitivity mode enabled: {e}")
            return None

    def get_is_high_sensitivity_mode_supported(self) -> Optional[bool]:
        """
        Check if the camera supports High Sensitivity Mode.

        Returns:
            Optional[bool]: True if supported.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return (
                    self._camera.camera.RemoteControl.CameraSettings.IsHighSensitivityModeSupported()
                )
        except Exception as e:
            self.logger.error(f"Error checking high sensitivity mode supported: {e}")
            return None

    def get_is_shutter_enabled(self) -> Optional[bool]:
        """
        Check if shutter is enabled.

        Returns:
            Optional[bool]: True if shutter is enabled.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return (
                    self._camera.camera.RemoteControl.CameraSettings.IsShutterEnabled()
                )
        except Exception as e:
            self.logger.error(f"Error checking shutter enabled: {e}")
            return None

    def get_is_shutter_supported(self) -> Optional[bool]:
        """
        Check if shutter is supported.

        Returns:
            Optional[bool]: True if shutter is supported.

        Raises:
            InvalidOperationException: If the operation is invalid.
            CommandFailedException: If the command fails.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                return (
                    self._camera.camera.RemoteControl.CameraSettings.IsShutterSupported()
                )
        except Exception as e:
            self.logger.error(f"Error checking shutter supported: {e}")
            return None

    """ Set methods """

    def set_atmospheric_temperature(self, value: float) -> None:
        """
        Set the atmospheric temperature in the camera.

        Args:
            value (float): Temperature in Kelvin. Range 0 - 5000.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraSettings.SetAtmosphericTemperature(
                    value
                )
        except Exception as e:
            self.logger.error(f"Error setting atmospheric temperature: {e}")
            return None

    def set_external_optics_temperature(self, value: float) -> None:
        """
        Set the external optics temperature in the camera.

        Args:
            value (float): Temperature in Kelvin. Range 0 - 5000.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraSettings.SetExternalOpticsTemperature(
                    value
                )
        except Exception as e:
            self.logger.error(f"Error setting external optics temperature: {e}")
            return None

    def set_external_optics_transmission(self, value: float) -> None:
        """
        Set the external optics transmission in the camera.

        Args:
            value (float): Transmission in percentage. Range 0.1 - 100.0%.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraSettings.SetExternalOpticsTransmission(
                    value
                )
        except Exception as e:
            self.logger.error(f"Error setting external optics transmission: {e}")
            return None

    def set_ext_opt_trans_alt_val(self, value: float) -> None:
        """
        Set the external optics (window) transmission.

        This method sets the transmission value for external optics/window.
        Not all camera models support this feature.

        Args:
            value (float): Transmission value. Range 0.1 to 1.0.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                # Check if the camera supports external optics transmission
                if not hasattr(
                    self._camera.camera.RemoteControl.CameraSettings,
                    "SetExtOptTransAltVal",
                ):
                    self.logger.warning(
                        "Camera does not support setting external optics transmission"
                    )
                    return None

                self._camera.camera.RemoteControl.CameraSettings.SetExtOptTransAltVal(
                    value
                )
        except Exception as e:
            self.logger.warning(
                f"Setting external optics transmission not supported or failed: {e}"
            )
            return None

    def set_high_sensitivity_mode_enabled(self, enable: bool) -> None:
        """
        Enable or disable High Sensitivity Mode.

        Args:
            enable (bool): Enable or disable HSM.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraSettings.SetHighSensitivityModeEnabled(
                    enable
                )
        except Exception as e:
            self.logger.error(f"Error setting high sensitivity mode enabled: {e}")
            return None

    def set_is_ext_opt_transm_alt_active(self, is_enabled: bool) -> None:
        """
        Enable or disable external optics (window).

        This method enables/disables external optics/window transmission.
        Not all camera models support this feature.

        Args:
            is_enabled (bool): True to enable, False to disable.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                # Check if the camera supports this feature
                if not hasattr(
                    self._camera.camera.RemoteControl.CameraSettings,
                    "SetIsExtOptTransmAltActive",
                ):
                    self.logger.warning(
                        "Camera does not support setting external optics transmission"
                    )
                    return None

                self._camera.camera.RemoteControl.CameraSettings.SetIsExtOptTransmAltActive(
                    is_enabled
                )
        except Exception as e:
            self.logger.warning(
                f"Setting external optics transmission not supported or failed: {e}"
            )
            return None

    def set_object_distance(self, value: float) -> None:
        """
        Set the object distance in the camera.

        Args:
            value (float): Distance in meters. Range 0 - 10000.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraSettings.SetObjectDistance(
                    value
                )
        except Exception as e:
            self.logger.error(f"Error setting object distance: {e}")
            return None

    def set_object_emissivity(self, value: float) -> None:
        """
        Set the object emissivity in the camera.

        Args:
            value (float): Emissivity. Range 0.01 - 1.00.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraSettings.SetObjectEmissivity(
                    value
                )
        except Exception as e:
            self.logger.error(f"Error setting object emissivity: {e}")
            return None

    def set_palette_by_name(self, name: str) -> None:
        """
        Select palette by name.

        Args:
            name (str): Palette filename in the camera.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraSettings.SetPaletteByName(name)
        except Exception as e:
            self.logger.error(f"Error setting palette by name: {e}")
            return None

    def set_reference_temperature(self, value: float) -> None:
        """
        Set the reference temperature in the camera.

        Args:
            value (float): Temperature in Kelvin. Range 0 - 5000.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraSettings.SetReferenceTemperature(
                    value
                )
        except Exception as e:
            self.logger.error(f"Error setting reference temperature: {e}")
            return None

    def set_reflected_temperature(self, value: float) -> None:
        """
        Set the reflected temperature in the camera.

        Args:
            value (float): Temperature in Kelvin. Range 0 - 5000.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraSettings.SetReflectedTemperature(
                    value
                )
        except Exception as e:
            self.logger.error(f"Error setting reflected temperature: {e}")
            return None

    def set_relative_humidity(self, value: float) -> None:
        """
        Set the relative humidity in the camera.

        Args:
            value (float): Humidity in percentage. Range 0.1 - 100.0%.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraSettings.SetRelativeHumidity(
                    value
                )
        except Exception as e:
            self.logger.error(f"Error setting relative humidity: {e}")
            return None

    def set_scale_adjust_enabled(self, value: bool) -> None:
        """
        Enable or disable the scale adjust mode.

        Args:
            value (bool): True to enable, False to disable.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraSettings.SetScaleAdjustEnabled(
                    value
                )
        except Exception as e:
            self.logger.error(f"Error setting scale adjust enabled: {e}")
            return None

    def set_send_lens_temp(self, value: bool) -> None:
        """
        Enable or disable the virtual temperature sensor.

        Args:
            value (bool): True to activate, False to deactivate.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraSettings.SetSendLensTemp(value)
        except Exception as e:
            self.logger.error(f"Error setting send lens temp: {e}")
            return None

    def set_shutter_enabled(self, enable: bool) -> None:
        """
        Enable or disable the shutter.

        Args:
            enable (bool): True to enable, False to disable.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraSettings.SetShutterEnabled(
                    enable
                )
        except Exception as e:
            self.logger.error(f"Error setting shutter enabled: {e}")
            return None

    def set_temperature_range_index(self, index: int) -> None:
        """
        Set the temperature range index.

        Args:
            index (int): Zero based index.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraSettings.SetTemperatureRangeIndex(
                    index
                )
        except Exception as e:
            self.logger.error(f"Error setting temperature range index: {e}")
            return None

    def set_t_lens_ext(self, value: float) -> None:
        """
        Set the external temperature sensor (sets the external optics/window temperature).

        Args:
            value (float): Temperature in Kelvin.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraSettings.SetTLensExt(value)
        except Exception as e:
            self.logger.error(f"Error setting T lens ext: {e}")
            return None

    def set_zoom_factor(self, value: float) -> None:
        """
        Set the zoom factor in the camera.

        Args:
            value (float): Zoom factor.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraSettings.SetZoomFactor(value)
        except Exception as e:
            self.logger.error(f"Error setting zoom factor: {e}")
            return None

    def set_distance_unit(self, unit: str) -> None:
        """
        Set the distance unit used in the camera.

        Args:
            unit (str): The distance unit to set.

        Raises:
            ArgumentOutOfRangeException: If the argument is out of range.
            InvalidOperationException: If the operation is invalid.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraSettings.SetDistanceUnit(unit)
        except Exception as e:
            self.logger.error(f"Error setting distance unit: {e}")
            return None

    def set_scale_adjust_mode(self, mode: str) -> None:
        """
        Set the scale adjust mode.

        Args:
            mode (str): The scale adjust mode to set.

        Raises:
            InvalidOperationException: If the operation is invalid.
            ArgumentOutOfRangeException: If the argument is out of range.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraSettings.SetScaleAdjustMode(
                    mode
                )
        except Exception as e:
            self.logger.error(f"Error setting scale adjust mode: {e}")
            return None

    def set_scale_limits(self, limits: str) -> None:
        """
        Set the scale limits in the camera.

        Args:
            limits (str): Temperature range in Kelvin. Range 0 - 5000.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraSettings.SetScaleLimits(limits)
        except Exception as e:
            self.logger.error(f"Error setting scale limits: {e}")
            return None

    def set_temperature_unit(self, unit: str) -> None:
        """
        Set the display temperature unit in the camera.

        Args:
            unit (str): Fahrenheit or Celsius are supported values for temperature unit.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraSettings.SetTemperatureUnit(
                    unit
                )
        except Exception as e:
            self.logger.error(f"Error setting temperature unit: {e}")
            return None

    def set_video_mode(self, mode: str) -> None:
        """
        Set the camera video mode (PAL or NTSC).

        Args:
            mode (str): The video mode to set.

        Raises:
            ArgumentOutOfRangeException: If the argument is out of range.
            InvalidOperationException: If the operation is invalid.
        """
        try:
            if not self._check_camera_ready():
                return None

            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraSettings.SetVideoMode(mode)
        except Exception as e:
            self.logger.error(f"Error setting video mode: {e}")
            return None

    def to_string(self) -> dict:
        """
        Return all properties in JSON format.

        Returns:
            dict: JSON string of all properties.
        """
        return {
            "atmospheric_temperature": self.atmospheric_temperature,
            "distance_unit": self.distance_unit,
            "external_optics_temperature": self.external_optics_temperature,
            "external_optics_transmission": self.external_optics_transmission,
            "ext_opt_trans_alt_val": self.ext_opt_trans_alt_val,
            "is_ext_opt_transm_alt_active": self.is_ext_opt_transm_alt_active,
            "is_scale_adjust_enabled": self.is_scale_adjust_enabled,
            "object_distance": self.object_distance,
            "object_emissivity": self.object_emissivity,
            "palette_name": self.palette_name,
            "reference_temperature": self.reference_temperature,
            "reflected_temperature": self.reflected_temperature,
            "relative_humidity": self.relative_humidity,
            "scale_adjust_mode": self.scale_adjust_mode,
            "scale_limits": self.scale_limits,
            "send_lens_temp": self.send_lens_temp,
            "temperature_range_index": self.temperature_range_index,
            "temperature_unit": self.temperature_unit,
            "time_until_camera_is_ready": self.time_until_camera_is_ready,
            "t_lens_ext": self.t_lens_ext,
            "video_mode": self.video_mode,
            "zoom_factor": self.zoom_factor,
            "is_battery_charging": self.is_battery_charging,
            "is_high_sensitivity_mode_enabled": self.is_high_sensitivity_mode_enabled,
            "is_high_sensitivity_mode_supported": self.is_high_sensitivity_mode_supported,
            "is_shutter_enabled": self.is_shutter_enabled,
            "is_shutter_supported": self.is_shutter_supported,
        }
