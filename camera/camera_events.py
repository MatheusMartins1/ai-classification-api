"""
Developer: Matheus Martins da Silva
Creation Date: 2025-07-18
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva.
"""

# System imports
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

# Third-party imports
import clr

# Project imports
from config.settings import settings

# Add references to DLLs
dll_path = os.path.join(settings.BASE_DIR, "ThermalCameraLibrary")
clr.AddReference(os.path.join(dll_path, "ThermalCamera.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Live.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Image.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Gigevision.dll"))
clr.AddReference("System")

import Flir.Atlas.Gigevision as Gigevision  # type: ignore
import Flir.Atlas.Image as Image  # type: ignore

# Import Flir SDK
import Flir.Atlas.Live as live  # type: ignore
import System  # type: ignore
from redis_service.managers.redis_manager import RedisManager

import camera.image.image as image_handler
import camera.palettes.palettes as palettes_handler
from camera.image.alarms import alarm as alarm_handler
from camera.image.image_service import ImageDataService
from camera.image.measurements import measurements as measurements_handler

# Local imports
from utils.LoggerConfig import LoggerConfig

logger = LoggerConfig.add_file_logger(
    name="camera_events", filename=None, dir_name=None, prefix="camera"
)

redis_manager = RedisManager()


class CameraEventManager:
    """
    Manages all camera events and their handlers.
    Centralizes event registration and handling for better organization.
    """

    def __init__(self, _camera: Any) -> None:
        """
        Initialize the event manager.

        Args:
            camera: Camera instance to manage events for
        """
        self._camera = _camera
        self._registered_events: Set[str] = set()
        self._event_handlers: Dict[str, Any] = {}  # Strong references to event handlers
        self.logger = logger

    def setup_generic_event_capture(self) -> None:
        """
        Setup generic event capture for all available camera events.
        Based on Flir.Atlas.Live namespace and subcategories.
        """
        try:
            if not self._camera:
                logger.warning("Camera not initialized")
                return

            for event_name in self.CAMERA_EVENTS:
                try:
                    if hasattr(self._camera, event_name):
                        event = getattr(self._camera, event_name)
                        if (
                            event_name not in self.HANDLED_EVENTS
                        ):  # Skip already handled events
                            # Create and store handler reference
                            handler = self.capture_generic_event
                            self._event_handlers[f"generic_{event_name}"] = handler
                            event += handler
                            self._registered_events.add(event_name)
                            logger.info(
                                f"Registered generic handler for event: {event_name}"
                            )
                except Exception as e:
                    logger.debug(
                        f"Event {event_name} not available: {e}"
                    )  # Debug level since not all cameras support all events

        except Exception as e:
            logger.error(f"Error setting up generic event capture: {e}")

    def capture_generic_event(self, sender: Any, e: Any) -> bool:
        """
        Generic event handler to capture and log any camera events.
        Handles events from Flir.Atlas.Live namespace.

        Args:
            sender: Event sender object (usually Camera instance)
            e: Event arguments specific to the event type

        Returns:
            bool: True if event was handled successfully, False otherwise
        """
        try:
            event_name = e.__class__.__name__
            event_data: Dict[str, str] = {}

            # Try to extract common event properties
            for prop in dir(e):
                if not prop.startswith("_"):  # Skip private properties
                    try:
                        value = getattr(e, prop)
                        if not callable(value):  # Skip methods
                            event_data[prop] = str(value)
                    except Exception:
                        pass

            logger.info(
                f"Generic event captured - Type: {event_name} | "
                f"Sender: {sender.__class__.__name__ if sender else 'None'} | "
                f"Data: {event_data}"
            )

            return True  # Return True to acknowledge event handling

        except Exception as ex:
            logger.error(f"Error in generic event handler: {ex}")
            return False

    def get_registered_events(self) -> Set[str]:
        """
        Get list of successfully registered events.

        Returns:
            Set[str]: Set of event names that were successfully registered
        """
        return self._registered_events.copy()

    def cleanup(self) -> None:
        """
        Cleanup event handlers and registrations.
        Should be called when disconnecting from camera.
        """
        try:
            self._camera.set_image_ready(False)

            # Cleanup generic handlers
            for event_name in self._registered_events:
                try:
                    if hasattr(self._camera, event_name):
                        event = getattr(self._camera, event_name)
                        handler = self._event_handlers.get(f"generic_{event_name}")
                        if handler:
                            event -= handler
                        logger.info(f"Unregistered handler for event: {event_name}")
                except Exception as e:
                    logger.error(
                        f"Error unregistering handler for event {event_name}: {e}"
                    )

            self._registered_events.clear()
            self._event_handlers.clear()

        except Exception as e:
            logger.error(f"Error during event cleanup: {e}")

        redis_manager.publish_message(
            operation_type="camera_connection",
            action="disconnect",
            data={"force_cleanup": True},
            origin="camera_events",
        )

    # Specific Event Handlers

    def on_device_error(self, sender: Any, e) -> None:
        """
        Handle device error events.

        Args:
            sender: Event sender
            e: Device error event arguments
        """
        try:
            DeviceErrorType = live.Device.CameraBase.DeviceError

            # if isinstance(sender,live.Device.ThermalCamera):
            #     DeviceErrorType = live.Device.ThermalCamera.DeviceError
            # elif isinstance(sender,live.Device.Camera):
            #     DeviceErrorType = live.Device.Camera.DeviceError
            # elif isinstance(sender,live.Device.VideoOverlayCamera):
            #     DeviceErrorType = live.Device.VideoOverlayCamera.DeviceError
            # elif isinstance(sender,live.Device.StreamingCamera):
            #     DeviceErrorType = live.Device.StreamingCamera.DeviceError

            # Create and store handler reference if not exists
            if "device_error" not in self._event_handlers:
                handler = System.EventHandler[DeviceErrorType](self.on_device_error)
                self._event_handlers["device_error"] = handler
                # self._camera.camera.DeviceError = handler

            self.logger.error(f"Device error: {str(e)}")
        except Exception as ex:
            self.logger.error(f"Failed to log device error: {str(ex)}")

    def on_connection_status_changed(self, sender: Any, e) -> None:
        """
        Handle connection status change events.

        Args:
            sender: Event sender
            e: Connection status event arguments
        """
        try:
            # Create and store handler reference if not exists
            if "connection_status" not in self._event_handlers:
                handler = System.EventHandler[live.Device.ConnectionStatus](
                    self.on_connection_status_changed
                )
                self._event_handlers["connection_status"] = handler
                # self._camera.camera.ConnectionStatusChanged = handler

            self.logger.info(f"Connection status: {e.Status}")
            self._camera.is_connected = self._camera.camera.IsConnected

            if e.Status == live.Device.ConnectionStatus.Disconnecting:
                # ws.publish("connection_status", {"status": "Disconnecting"})
                pass
            if e.Status == live.Device.ConnectionStatus.Connecting:
                # ws.publish("connection_status", {"status": "Connecting"})
                pass

            if e.Status == live.Device.ConnectionStatus.Connected:
                # self._camera.ui_manager.start_elapsed_time()
                self._camera.connection_status = "Connected"
                # ws.publish("connection_status", {"status": "Connected"})
            if e.Status == live.Device.ConnectionStatus.Disconnected:
                # self._camera.ui_manager.stop_elapsed_time()
                self._camera.connection_status = "Disconnected"
                self._camera.connection_manager._handle_hardware_disconnect()
                # ws.publish("connection_status", {"status": "Disconnected"})
            else:
                # self._camera.ui_manager.stop_elapsed_time()
                pass

        except Exception as ex:
            self.logger.error(f"Error handling connection status change: {str(ex)}")

    def on_image_received(self, sender: Any, e) -> None:
        """
        Handle image received events.

        Args:
            sender: Event sender
            e: Image received event arguments
        """
        pass
        # try:
        # TODO: handle this properly
        # event_types = [
        #     live.Device.DualImageReceivedEventArgs,
        #     live.Device.Camera.ImageReceived,
        #     # CameraAdapter_ImageReady
        # ]

        # matching_types = [t for t in event_types if isinstance(e, t)]
        # if matching_types:
        #     current_event_type = matching_types[0]
        # else:
        #     current_event_type = live.Device.Camera.ImageReceived

        # current_event_type = live.Device.Camera.ImageReceived
        # event_type = type(e)
        # if event_type not in event_types:
        #     self.logger.warning(
        #         f"Unexpected event type: {event_type.__name__}. Expected one of {event_types}"
        #     )
        #     return

        # Create and store handler reference if not exists
        # if "image_received" not in self._event_handlers:
        # handler = System.EventHandler[current_event_type](
        #     self.on_image_received
        # )
        # self._event_handlers["image_received"] = handler
        # self._camera.camera.ImageReceived = handler

        # self.logger.info(f"Image received event triggered - {e}")
        #     if not self._camera.camera.IsConnected:
        #         return

        #     if self._camera.is_load_disabled:
        #         return

        #     # self._camera.refresh_ui = True
        # except Exception as ex:
        #     self.logger.error(f"Error handling image received event: {str(ex)}")

    def on_image_initialized(self, sender: Any, e) -> None:
        """
        Handle image initialized events.

        Args:
            sender: Event sender
            e: Image initialized event arguments
        """
        self.logger.info(f"Image initialized event triggered - {e}")
        if not self._camera.camera.IsConnected:
            self.logger.error("Error: Camera disconnected")
            return

        max_retries = 10
        wait_time = 1

        for attempt in range(max_retries):
            if self._camera.image_obj_thermal or self._camera.image_obj_visual:
                self.logger.info("Image objects already available")
                break

            with self._camera._locks("image"):
                self.logger.info(
                    f"Checking grabber state: {self._camera.camera.IsGrabberReady}"
                )

                if self._camera.camera.IsGrabberReady == live.Device.GrabberState.Ready:
                    # Validate and get image objects using ImageExtractor
                    thermal_obj, visual_obj = (
                        self._camera.image_extractor.get_image_objects(validate=True)
                    )

                    if thermal_obj:
                        self._camera.image_obj_thermal = thermal_obj

                    if visual_obj:
                        self._camera.image_obj_visual = visual_obj

                    if self._camera.image_obj_thermal or self._camera.image_obj_visual:
                        break
                    else:
                        self.logger.warning(
                            "Image objects not available after validation"
                        )
                else:
                    self.logger.warning(
                        f"Grabber not ready - state: {self._camera.camera.IsGrabberReady}"
                    )

            self.logger.info(
                f"Waiting for image objects... Attempt {attempt + 1} of {max_retries}"
            )
            time.sleep(wait_time)
            wait_time = min(wait_time * 2, 30)

        if not self._camera.image_obj_thermal and not self._camera.image_obj_visual:
            # Final attempt using ImageExtractor with validation
            self.logger.info("Final attempt to get image objects with validation")
            thermal_obj, visual_obj = self._camera.image_extractor.get_image_objects(
                validate=True
            )

            if thermal_obj:
                self._camera.image_obj_thermal = thermal_obj
            if visual_obj:
                self._camera.image_obj_visual = visual_obj

        image = (
            self._camera.image_obj_thermal
            if self._camera.image_obj_thermal
            else self._camera.image_obj_visual
        )

        if image is None:
            self.logger.error("Image objects not available after all retries")
            self._camera.set_image_ready(False)
            return

        self._camera.set_image_ready(True)

        try:
            # Initialize camera settings and handlers
            self._camera.camera_control.camera_control_settings.update_settings()
        except Exception as e:
            self.logger.critical(f"Error updating camera settings: {e}")

        if self._camera.is_thermal_image_supported:
            self._camera.is_image_initialized = True
            # Initialize handlers
            self._camera.camera_image_handler = image_handler.ImageHandler(self._camera)
            self._camera.alarms_handler = alarm_handler.Alarm(self._camera)
            self._camera.measurements_handler = measurements_handler.CameraMeasurements(
                self._camera
            )
            self._camera.palettes_handler = palettes_handler.PaletteHandler(
                self._camera
            )

            self._camera.image_service = ImageDataService(self._camera)
            self._camera.image_service._initialize_standalone_resources(
                thermal_image=self._camera.image_obj_thermal, camera=self._camera
            )

            # Update image and settings
            self._camera.camera_image_handler.update_image(image)
            self._camera.measurements_handler.update_settings()

            # Setup alarm event handlers
            self._camera.image_obj_thermal.Alarms.Changed += (
                self._camera.alarms_handler.on_alarm_event_change
            )
            self._camera.image_obj_thermal.Alarms.Removed += (
                self._camera.alarms_handler.on_alarm_removed_event
            )

            # Setup isotherm event handlers
            self._camera.image_obj_thermal.Isotherms.Changed += (
                self._camera.alarms_handler.on_alarm_iso_event_change
            )
            self._camera.image_obj_thermal.Isotherms.Removed += (
                self._camera.alarms_handler.on_alarm_removed_event
            )

            try:
                self._camera.connection_manager.fill_camera_info()
            except Exception as e:
                self.logger.error(f"Error filling camera info - {e}")

        if hasattr(image, "EnterLock"):
            image.EnterLock()
        try:
            if isinstance(image, Image.ThermalImage):
                image.Scale.IsAutoAdjustEnabled = True
        finally:
            if hasattr(image, "ExitLock"):
                image.ExitLock()

        self._camera.is_initialized = True

        # TODO: add type:live.Discovery.CameraDiscovered or similar

    def on_device_found(self, sender: Any, e) -> None:
        """
        Handle device found events.

        Args:
            sender: Event sender
            e: Device found event arguments
        """
        if e.Device not in self._camera.connection_manager.devices:
            self._camera.connection_manager.devices.append(e.Device)
        self.logger.info(f"Device found: {e.Device.Name}")
        self._camera.connection_manager.scanner_status = "Done"

    # TODO: add type e: live.Discovery.CameraLost or similar
    def on_device_lost(self, sender: Any, e) -> None:
        """
        Handle device lost events.

        Args:
            sender: Event sender
            e: Device lost event arguments
        """
        self._camera.set_image_ready(False)
        self._camera.is_image_initialized = False
        self._camera.is_initialized = False
        self._camera.is_connected = False
        self._camera.connection_status = "Disconnected"
        self._camera.connection_manager.devices = [
            device
            for device in self._camera.connection_manager.devices
            if device.DeviceId != e.Device.DeviceId
        ]
        self.logger.info(f"Device lost: {e.Device.Name}")

        redis_manager.publish_message(
            operation_type="camera_connection",
            action="disconnect",
            data={"force_cleanup": True},
            origin="device_lost",
        )

        self._camera.connection_manager._handle_hardware_disconnect()

    # Events that already have specific handlers
    HANDLED_EVENTS: Set[str] = {
        "ConnectionStatusChanged",
        "ImageReceived",
        "ImageInitialized",
        "DeviceError",
        "DeviceFound",
        "DeviceLost",
    }
    """
    TODO:
        ThermalException
        ScaleChangedEventArgs
        TemperatureUnitEventArgs?
    """

    # Comprehensive dictionary of all possible camera events with SDK descriptions
    CAMERA_EVENTS: Dict[str, Dict[str, Any]] = {
        # Base Camera Events
        "ConnectionStatusChanged": {
            "description": "This event is fired when the connection status has changed.",
            "name": "ConnectionStatusChanged",
            "type": live.Device.ConnectionStatus,
            "category": "Base",
        },
        "DeviceError": {
            "description": "This event is fired when an error is detected.",
            "name": "DeviceError",
            "type": live.Device.CameraBase.DeviceError,
            "category": "Base",
        },
        # Image Events
        "ImageReceived": {
            "description": "This event is fired when a new image is received from the camera.",
            "name": "ImageReceived",
            "type": live.Device.Camera.ImageReceived,
            "category": "Image",
        },
        "ImageInitialized": {
            "description": "This event is fired when the image is initialized and ready for processing.",
            "name": "ImageInitialized",
            "type": live.Device.Camera.ImageInitialized,
            "category": "Image",
        },
        "ImageParametersChanged": {
            "description": "This event is fired when image parameters have been modified.",
            "name": "ImageParametersChanged",
            "type": Image.ImageParameters.ImageParametersChanged,
            "category": "Image",
        },
        "ScaleImageChanged": {
            "description": "This event is fired when the scale image has changed.",
            "name": "ScaleImageChanged",
            "type": Image.Scale.ScaleImageChanged,
            "category": "Image",
        },
        # Collection Events
        "Added": {
            "description": "This event is fired when an item is added to a collection.",
            "name": "Added",
            "type": Image.Alarms.AlarmCollection.Added,
            "category": "Collection",
        },
        "Changed": {
            "description": "This event is fired when an item in a collection is changed.",
            "name": "Changed",
            "type": Image.Alarms.AlarmCollection.Changed,
            "category": "Collection",
        },
        "Removed": {
            "description": "This event is fired when an item is removed from a collection.",
            "name": "Removed",
            "type": Image.Alarms.AlarmCollection.Removed,
            "category": "Collection",
        },
        # Discovery Events
        "DeviceFound": {
            "description": "This event is fired when a device is discovered.",
            "name": "DeviceFound",
            "type": live.Discovery.Discovery.DeviceFound,
            "category": "Discovery",
        },
        "DeviceLost": {
            "description": "This event is fired when a device is no longer available.",
            "name": "DeviceLost",
            "type": live.Discovery.Discovery.DeviceLost,
            "category": "Discovery",
        },
        "GigabitCameraDetected": {
            "description": "This event is fired when a GigE camera is detected.",
            "name": "GigabitCameraDetected",
            "type": live.Discovery.GigabitScanner.GigabitCameraDetected,
            "category": "Discovery",
        },
        "GigabitCameraLost": {
            "description": "This event is fired when a GigE camera is lost.",
            "name": "GigabitCameraLost",
            "type": live.Discovery.GigabitScanner.GigabitCameraLost,
            "category": "Discovery",
        },
        "NetworkCameraDetected": {
            "description": "This event is fired when a network camera is detected.",
            "name": "NetworkCameraDetected",
            "type": live.Discovery.NetworkScanner.NetworkCameraDetected,
            "category": "Discovery",
        },
        "NetworkCameraLost": {
            "description": "This event is fired when a network camera is lost.",
            "name": "NetworkCameraLost",
            "type": live.Discovery.NetworkScanner.NetworkCameraLost,
            "category": "Discovery",
        },
        "UsbCameraDetected": {
            "description": "This event is fired when a USB camera is detected.",
            "name": "UsbCameraDetected",
            "type": live.Discovery.UsbScanner.UsbCameraDetected,
            "category": "Discovery",
        },
        "UsbCameraLost": {
            "description": "This event is fired when a USB camera is lost.",
            "name": "UsbCameraLost",
            "type": live.Discovery.UsbScanner.UsbCameraLost,
            "category": "Discovery",
        },
        # Streaming Events
        "FrameReceived": {
            "description": "This event is fired when a new frame is received from the GigE Vision stream.",
            "name": "FrameReceived",
            "type": Gigevision.Streaming.GigeVisionStream.FrameReceived,
            "category": "Streaming",
        },
        "ThermalFrameReceived": {
            "description": "This event is fired when a new thermal frame is received.",
            "name": "ThermalFrameReceived",
            "type": Gigevision.Streaming.ThermalStream.ThermalFrameReceived,
            "category": "Streaming",
        },
        "StreamError": {
            "description": "This event is fired when a streaming error occurs.",
            "name": "StreamError",
            "type": live.Device.Camera.StreamError,
            "category": "Streaming",
        },
        "StreamsUpdated": {
            "description": "This event is fired when available streams are updated.",
            "name": "StreamsUpdated",
            "type": live.Device.StreamingCamera.StreamsUpdated,
            "category": "Streaming",
        },
        # Playback Events
        "SelectedIndexChanged": {
            "description": "This event is fired when the selected frame index changes in the sequence player.",
            "name": "SelectedIndexChanged",
            "type": Image.Playback.ThermalSequencePlayer.SelectedIndexChanged,
            "category": "Playback",
        },
        "StatusChanged": {
            "description": "This event is fired when the player status changes.",
            "name": "StatusChanged",
            "type": Image.Playback.ThermalSequencePlayer.StatusChanged,
            "category": "Playback",
        },
        # Remote Control Events
        "CommandExecuted": {
            "description": "This event is fired when a remote command is executed.",
            "name": "CommandExecuted",
            "type": live.Remote.RemoteControl.CommandExecuted,
            "category": "RemoteControl",
        },
        # Temperature Events
        "TemperatureUnitChanged": {
            "description": "This event is fired when the temperature unit is changed.",
            "name": "TemperatureUnitChanged",
            "type": Image.ThermalImage.TemperatureUnitChanged,
            "category": "Temperature",
        },
        # External Trigger Events
        "TriggerChangedDigitalPort1": {
            "description": "This event is fired when the digital port 1 trigger state changes.",
            "name": "TriggerChangedDigitalPort1",
            "type": live.Device.ExternalTrigger.TriggerChangedDigitalPort1,
            "category": "ExternalTrigger",
        },
        # Logging Events
        "Updated": {
            "description": "This event is fired when the log is updated.",
            "name": "Updated",
            "type": live.Log.LogWriter.Updated,
            "category": "Logging",
        },
        # FIXME: FIX this
        # UI Events (WinForms)
        # "DeviceSelectedEvent": {
        #     "description": "This event is fired when a device is selected in the thermal scanner control.",
        #     "name": "DeviceSelectedEvent",
        #     "type": live.WinForms.ThermalScannerControl.DeviceSelected,
        #     "category": "UI"
        # },
        # "MouseDoubleClickEvent": {
        #     "description": "This event is fired when a mouse double click occurs in the discovery control.",
        #     "name": "MouseDoubleClickEvent",
        #     "type": live.WinForms.DiscoveryControl.MouseDoubleClick,
        #     "category": "UI"
        # },
        # "SelectionChanged": {
        #     "description": "This event is fired when the selection changes in the discovery control.",
        #     "name": "SelectionChanged",
        #     "type": live.WinForms.DiscoveryControl.SelectionChanged,
        #     "category": "UI"
        # }
    }
