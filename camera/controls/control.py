"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

import datetime
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

import Flir.Atlas.Image as Image  # type: ignore

# Import the necessary classes from the assembly
import Flir.Atlas.Live as live  # type: ignore

from camera.controls.control_settings import CameraControlSettings
from camera.controls.focus import CameraControlFocus
from camera.controls.fusion_mode import CameraControlFusionMode
from camera.controls.location import CameraLocation


# TODO: Implement the CameraControl class
class CameraControl:
    def __init__(self, _camera):
        self._camera = _camera
        self.logger = _camera.logger

        self.camera_control_settings = CameraControlSettings(_camera)
        self.camera_control_focus = CameraControlFocus(_camera)
        self.camera_location = CameraLocation(_camera)
        self.camera_fusion_mode = CameraControlFusionMode(_camera)

        # TODO: Change to consume from the subclass
        self.is_nuc_supported = None
        self.is_focus_supported = None
        self.is_hsm_supported = None
        self.is_hsm_enabled = None
        self.is_dual_fov_supported = None
        self.is_recorder_supported = True
        self.is_snapshot_supported = True

    def set_camera(self, camera):
        """
        Set the camera object and configure event handlers.

        Args:
            camera: The camera object to set.
        """
        has_function = hasattr(self._camera, "camera_connection_status_changed")

        if self._camera is not None:
            self.update_buttons(self._camera.camera.ConnectionStatus)

    def update_buttons(self, connection_status):
        """
        Update the state of control buttons based on the connection status.

        Args:
            connection_status: The connection status of the camera.
        """
        if connection_status == live.Device.ConnectionStatus.Connected:

            with self._camera._locks("control"):
                self.is_nuc_supported = (
                    self._camera.camera.RemoteControl.CameraSettings.IsShutterSupported()
                )
                self.is_focus_supported = (
                    self._camera.camera.RemoteControl.Focus.IsSupported()
                )

                try:
                    is_recorder_supported = (
                        True if self._camera.camera.Recorder is not None else False
                    )
                    self.is_recorder_supported = is_recorder_supported
                except Exception as e:
                    self.is_recorder_supported = False
                    self.logger.error(f"e from CameraSettings: {e}")

                try:
                    self.is_hsm_supported = (
                        self._camera.camera.RemoteControl.CameraSettings.IsHighSensitivityModeSupported()
                        and self._camera.is_thermal_image_supported
                    )
                except Exception as e:
                    self.is_hsm_supported = False
                    self.logger.error(f"e from CameraSettings: {e}")

    def auto_adjust(self) -> None:
        """
        Perform a one-shot auto adjust of scale limits.

        Raises:
            InvalidOperationException: If the operation is invalid or not connected.
        """
        try:
            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraAction.AutoAdjust()
        except Exception as e:
            self.logger.error(f"Error performing auto adjust: {e}")
            return None

    def get_dual_fov_mode(self) -> None | live.Remote.DualFOVMode:
        """
        Get Dual FOV mode for cameras/lenses that support it.

        Returns:
            DualFOVMode: The current Dual FOV mode.

        Raises:
            InvalidOperationException: If the operation is invalid, not connected, or no Dual FOV lens is attached.

        Concerns
            Async
        """
        # TEST: Asynchronous function call
        try:
            with self._camera._locks("control"):
                return self._camera.camera.RemoteControl.CameraAction.GetDualFOVMode()
        except Exception as e:
            self.logger.error(f"Error getting Dual FOV mode: {e}")
            return None

    def get_is_dual_fov_supported(self) -> None | bool:
        """
        Check if dual FOV lens is attached and remote commands to change FOV are supported.

        Returns:
            bool: True if dual FOV is supported.

        Raises:
            InvalidOperationException: If the operation is invalid, not connected, or camera software does not support it.

        Concerns
            Async
        """
        # TEST: Asynchronous function call
        try:
            with self._camera._locks("control"):
                return (
                    self._camera.camera.RemoteControl.CameraAction.IsDualFOVSupported()
                )
        except Exception as e:
            self.logger.error(f"Error checking if dual FOV is supported: {e}")
            return None

    def nuc(self) -> None:
        """
        Perform a one-point NUC (Non-uniformity correction) with a black body method.

        Raises:
            InvalidOperationException: If the operation is invalid or not connected.

        Concerns
            Async
        """
        # TEST: Asynchronous function call

        try:
            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraAction.Nuc()
        except Exception as e:
            self.logger.error(f"Error performing NUC: {e}")
            return None

    def set_calibration_data(self, R: float, B: float, F: float, O: float) -> None:
        """
        Set calibration data.

        Args:
            R (float): Calibration parameter R.
            B (float): Calibration parameter B.
            F (float): Calibration parameter F.
            O (float): Calibration parameter O.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraAction.SetCalibrationData(
                    R, B, F, O
                )
        except Exception as e:
            self.logger.error(f"Error setting calibration data: {e}")
            return None

    def set_dual_fov_mode(self, mode: str):
        """
        Set FOV for cameras/lenses that support it.

        Args:
            mode (DualFOVMode): The new FOV Mode setting.

        Raises:
            InvalidOperationException: If the operation is invalid, not connected, or no Dual FOV lens is attached.
        """

        modes = {
            "Wide": live.Remote.DualFOVMode.Wide,
            "Tele": live.Remote.DualFOVMode.Tele,
        }

        dual_mode = live.Remote.DualFOVMode(modes[mode])

        try:
            with self._camera._locks("control"):
                self._camera.camera.RemoteControl.CameraAction.SetDualFOVMode(dual_mode)
            return True
        except Exception as e:
            self.logger.error(f"Error setting Dual FOV mode: {e}")
            return False

    def save_snapshot(self, filepath=None):
        """
        Save a snapshot. Image storage can take a few seconds.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

            filename = (
                filepath
                if filepath
                else os.path.join(
                    settings.BASE_DIR,
                    "static_media",
                    "snapshots",
                    f"snapshots_{self._camera.camera_serial}_{timestamp}.jpg",
                )
            )

            dir_path = os.path.dirname(filename)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)

            with self._camera._locks("image"):
                self._camera.image_obj_thermal.SaveSnapshot(filename)
            return True
        except Exception as e:
            self.logger.error(f"Error saving snapshot: {e}")
            raise e

    def recording_manager(self, action, config=None):
        """
        Centralized recording manager that handles all recording actions.

        Args:
            action (str): The recording action to perform ('start', 'stop', 'pause', 'continue')
            config (dict, optional): Configuration for recording (used mainly with 'start')

        Returns:
            dict: Response with status, message, and additional data
        """
        if not self._camera or not self._camera.camera:
            return {
                "status": False,
                "message": "Camera not available",
                "action": action,
            }

        try:
            with self._camera._locks("control"):
                # TODO: https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/class_flir_1_1_atlas_1_1_live_1_1_recorder_1_1_thermal_image_recorder.html
                recorder = self._camera.camera.Recorder

                if action == "start":
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = (
                        config.get("filepath")
                        if config and config.get("filepath")
                        else os.path.join(
                            settings.BASE_DIR,
                            "static_media",
                            "recordings",
                            f"rec_{self._camera.camera_serial}_{timestamp}.csq",
                        )
                    )

                    # Cria a pasta se não existir
                    dir_path = os.path.dirname(filename)
                    if not os.path.exists(dir_path):
                        os.makedirs(dir_path, exist_ok=True)

                    recorder.Start(filename)

                    if config and config.get("EnableTimeSpan"):
                        recorder.EnableTimeSpan(True)

                    if config and config.get("DisableTimeSpan"):
                        recorder.DisableTimeSpan(True)

                    return {
                        "status": True,
                        "message": "Recording started successfully",
                        "action": action,
                        "filename": os.path.basename(filename),
                        "filepath": filename,
                    }

                elif action == "stop":
                    recorder.Stop()
                    return {
                        "status": True,
                        "message": "Recording stopped successfully",
                        "action": action,
                    }

                elif action == "pause":
                    recorder.Pause()
                    return {
                        "status": True,
                        "message": "Recording paused successfully",
                        "action": action,
                    }

                elif action == "continue":
                    recorder.Continue()
                    return {
                        "status": True,
                        "message": "Recording continued successfully",
                        "action": action,
                    }

                else:
                    return {
                        "status": False,
                        "message": f"Unknown recording action: {action}",
                        "action": action,
                    }

        except Exception as e:
            self.logger.error(f"Recording {action} error: {e}")
            return {"status": False, "message": str(e), "action": action}

    def start_recording(self, config=None):
        """
        Start recording video.
        """
        result = self.recording_manager("start", config)
        if not result["status"]:
            raise Exception(result["message"])
        return result["status"]

    def stop_recording(self):
        """
        Stop recording video.
        """
        result = self.recording_manager("stop")
        if not result["status"]:
            raise Exception(result["message"])
        return result["status"]

    def pause_recording(self):
        """
        Pause recording video.
        """
        result = self.recording_manager("pause")
        if not result["status"]:
            raise Exception(result["message"])
        return result["status"]

    def continue_recording(self):
        """
        Continue recording video.
        """
        result = self.recording_manager("continue")
        if not result["status"]:
            raise Exception(result["message"])
        return result["status"]

    def hsm(self):
        """
        Toggle the High Sensitivity Mode (HSM) on the camera.

        This method checks if the High Sensitivity Mode (HSM) is currently enabled on the camera.
        If it is enabled, it disables it. If it is disabled, it enables it.

        Raises:
            AttributeError: If the camera object or its RemoteControl or CameraSettings attributes are not available.
        """
        if self._camera:

            with self._camera._locks("control"):
                is_hsm_enabled = (
                    self._camera.camera.RemoteControl.CameraSettings.IsHighSensitivityModeEnabled()
                )

                self.logger.info(
                    f"is_hsm_enabled - {is_hsm_enabled} | set to {not is_hsm_enabled}"
                )

                self._camera.camera.RemoteControl.CameraSettings.SetHighSensitivityModeEnabled(
                    not is_hsm_enabled
                )

    """
    TODO: FINISH IMPLEMENTATION - MASTER CLASS
    Flir.Atlas.Live.Remote Namespace Reference
    https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/namespace_flir_1_1_atlas_1_1_live_1_1_remote.html

    Classes
    class  	Command
        Base class for device command. More...
    
    class  	CommandExecutedEventArgs
        CommandExecutedEventArgs is returned after an executed camera command. More...
    
    class  	CommandFailedException
        Exception thrown when a remote command fails. More...
    
    class  	RemoteCameraControl
        Remote control. More...
    
    class  	RemoteCameraFocus
        Control the camera focus. More...
    
    class  	RemoteCameraGeoLocation
        Class for reading Geo Location data from a camera. More...
    
    class  	RemoteCameraSettings - DONE
    
    class  	RemoteControl
        Remote camera control. More...
    
    class  	RemoteFusionSettings
        Remote fusion modes. More...
    
    class  	RemoteHsi
        High speed interface. More...
    
    class  	WorkingEnvironment
        A working environment defines a valid combination of calibration case, frame rate and windowing mode. More...
    
    """

    """
    Flir.Atlas.Live.Remote Namespace Reference
    https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/namespace_flir_1_1_atlas_1_1_live_1_1_remote.html#a6c81223470a5caa9f6345c54a01dd1dd
    ◆ DisableContinuousFocus()
    void Flir.Atlas.Live.Remote.RemoteCameraFocus.DisableContinuousFocus	(		)	
    ◆ EnableContinuousFocus()
    void Flir.Atlas.Live.Remote.RemoteCameraFocus.EnableContinuousFocus	(		)	
    ◆ Mode()
    void Flir.Atlas.Live.Remote.RemoteCameraFocus.Mode	(	FocusMode	mode	)	
    ◆ SetDistance()
    void Flir.Atlas.Live.Remote.RemoteCameraFocus.SetDistance	(	double	distance	)	
    ◆ SetRoi()
    void Flir.Atlas.Live.Remote.RemoteCameraFocus.SetRoi	(	Rectangle	roi	)	
    ◆ SetSpeed()
    void Flir.Atlas.Live.Remote.RemoteCameraFocus.SetSpeed	(	int	speed	)	

    """

    """
    Flir.Atlas.Live.Remote.RemoteCameraControl Class Reference

    https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/class_flir_1_1_atlas_1_1_live_1_1_remote_1_1_remote_camera_control.html
    ◆ AutoAdjust()
    void Flir.Atlas.Live.Remote.RemoteCameraControl.AutoAdjust	(		)	
    ◆ Nuc()
    void Flir.Atlas.Live.Remote.RemoteCameraControl.Nuc	(		)	
    ◆ SaveSnapshot()
    void Flir.Atlas.Live.Remote.RemoteCameraControl.SaveSnapshot	(		)	
    ◆ SetCalibrationData()
    void Flir.Atlas.Live.Remote.RemoteCameraControl.SetCalibrationData	(	double	R,double	B,double	F,double	O )
    ◆ SetDualFOVMode()
    void Flir.Atlas.Live.Remote.RemoteCameraControl.SetDualFOVMode	(	DualFOVMode	mode	)	
    """

    """
    GPSInfo 	GetGpsInfo ()
 	Get GPS information from the camera.
 
    CompassInfo 	GetCompassInfo ()
        Class for reading compass data from a camera.
    """
