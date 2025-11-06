"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva.
"""

import os
import time

import clr

from config.settings import settings

# Add references to System for event handling
clr.AddReference("System")
import threading

import Flir.Atlas.Image as Image  # type: ignore

# Import Flir SDK
import Flir.Atlas.Live as live  # type: ignore
import System  # type: ignore
from System import EventHandler  # type: ignore

# Import local modules
import camera.camera_events as event_manager
from utils.LoggerConfig import LoggerConfig

connection_logger = LoggerConfig.add_file_logger(
    name="camera_connection", filename=None, dir_name=None, prefix="camera"
)


class CameraConnectionManager:
    def __init__(self, _camera):
        """Initialize the camera connection manager."""
        self._camera = _camera
        self.logger = _camera.logger
        self.is_connection_established = None

        self._heartbeat_thread = None
        self._heartbeat_stop_event = threading.Event()
        self._last_heartbeat = None
        self._heartbeat_interval = 1.0  # segundos
        self._heartbeat_timeout = 3.0  # segundos

        self.scanner = live.Discovery.ThermalCameraScanner()
        self.scanner_status = None

        # Use event manager handlers
        self.scanner.DeviceFound += self._camera.event_manager.on_device_found
        self.scanner.DeviceLost += self._camera.event_manager.on_device_lost

        # TODO: Implementar o scanner de rede
        # self.network_scanner = live.Discovery.NetworkScanner() Todo

        self.devices = []
        self.devices_list = []
        self.selected_device = None
        self.streaming_formats_supported = []
        self.streaming_format = None
        self.streaming_format_name = None

        # TODO: add self.selected_device.DeviceError += self.on_devide_error
        # self.selected_device.DeviceError += self.on_devide_error

    def _start_heartbeat(self):
        """Inicia o monitoramento de conexão por heartbeat"""
        if self._heartbeat_thread is not None and self._heartbeat_thread.is_alive():
            return

        self._heartbeat_stop_event.clear()
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_monitor, daemon=True
        )
        self._heartbeat_thread.start()
        connection_logger.info("Hardware connection monitoring started")

    def _stop_heartbeat_monitor(self):
        """Para o monitoramento de conexão"""
        if self._heartbeat_thread is not None:
            self._heartbeat_stop_event.set()
            self._heartbeat_thread.join(timeout=2.0)
            self._heartbeat_thread = None
            connection_logger.info("Hardware connection monitoring stopped")

    def _heartbeat_monitor(self):
        """Thread de monitoramento que verifica o estado real da câmera"""
        while not self._heartbeat_stop_event.is_set():
            try:
                if self._camera.camera is None:
                    continue

                # Verifica se a câmera ainda está fisicamente conectada
                is_alive = self._check_camera_hardware()

                if not is_alive and self.is_connection_established:
                    connection_logger.warning("Camera hardware disconnection detected")
                    self._handle_hardware_disconnect()

                self._last_heartbeat = time.time()

            except Exception as e:
                connection_logger.error(f"Error in heartbeat monitor: {e}")

            finally:
                # Aguarda próximo ciclo
                time.sleep(self._heartbeat_interval)

    def _check_camera_hardware(self) -> bool:
        """
        Verifica se a câmera ainda está fisicamente conectada.
        Retorna True se a câmera estiver OK, False se desconectada.
        """
        try:
            if not self._camera.camera:
                return False

            # Tenta acessar propriedades básicas da câmera
            # Se qualquer uma falhar, significa que a câmera foi desconectada
            checks = [
                lambda: self._camera.camera.IsConnected,
                # lambda: self._camera.camera.IsGrabberReady != live.Device.GrabberState.NotReady,
                # lambda: bool(self._camera.camera.GetHashCode()),  # Verifica se o objeto ainda é válido
            ]

            is_alive = all(check() for check in checks)

            # Se a câmera está viva mas ocupada, trata separadamente
            if is_alive and self._check_camera_busy():
                self._handle_camera_busy()

            return is_alive

        except Exception as e:
            connection_logger.debug(f"Hardware check failed: {e}")
            return False

    def _check_camera_busy(self) -> bool:
        """
        Verifica se a câmera está em estado 'busy'.

        Returns:
            bool: True se a câmera estiver ocupada, False caso contrário

        TODO: Implementar verificação completa de estados busy:
        - Durante NUC (Non-Uniformity Correction)
        - Durante Auto-Focus
        - Durante mudança de paleta
        - Durante mudança de configurações térmicas
        - Durante operações de I/O intensivas
        - Durante calibração
        - Quando buffer interno está cheio
        - Durante alterações de streaming format
        - Durante operações de gravação/snapshot
        """
        try:
            # TODO: Implementar verificação de estados busy
            # Exemplos de verificações a serem implementadas:
            # - self._camera.camera.IsPerformingNUC
            # - self._camera.camera.IsAutoFocusing
            # - self._camera.camera.IsCalibrating
            # - self._camera.camera.IsStreaming and self._camera.camera.StreamBufferFull
            # - etc.
            return False
        except Exception as e:
            connection_logger.debug(f"Busy check failed: {e}")
            return False

    def _handle_camera_busy(self) -> None:
        """
        Lida com o estado 'busy' da câmera.

        TODO: Implementar tratamento adequado para cada tipo de estado busy:
        1. Logging apropriado do tipo de operação em andamento
        2. Timeout adequado para cada tipo de operação
        3. Retry logic se necessário
        4. Notificação do sistema sobre o estado
        5. Possível pausa em operações não-críticas
        6. Verificação de deadlock/timeout
        7. Recovery automático se necessário
        8. Priorização de operações
        """
        # TODO: Implementar lógica de tratamento de estado busy
        connection_logger.debug(
            "Camera busy state detected - handler not implemented yet"
        )

    def _handle_hardware_disconnect(self):
        """
        Lida com desconexão física da câmera
        """
        try:
            connection_logger.warning("Handling hardware disconnection")

            self._camera.set_image_ready(False)
            self.is_connection_established = False
            self._camera.is_connected = False
            self._camera.connection_status = "Disconnected"
            self._camera.is_image_initialized = False
            self._camera.is_initialized = False

            connection_logger.info("Camera hardware disconnect handled")

            self._camera.event_manager.cleanup()

        except Exception as e:
            connection_logger.error(f"Error handling hardware disconnect: {e}")

    def fetch_resources(
        self,
        selected_format=None,
        force_scan=False,
        reconnect=False,
        chosen_device=None,
    ):
        if reconnect:
            self.logger.info("Reconnecting to camera")
            self.disconnect()
            self.is_connection_established = False
        else:
            if self.is_connection_established or self._camera.is_connected:
                self.logger.info("Connection already established")
                return True

        # If force_scan is True, reset the scanner and devices
        if force_scan:
            self.scanner_status = None
            self.devices = []
            self.devices_list = []
            self.selected_device = None
            self.streaming_formats_supported = []
            self.streaming_format = None
            self.streaming_format_name = None

        # Start scanning for devices
        if not self.scanner_status:
            self.start_scanning()

        max_wait = 30  # seconds
        start_time = time.time()
        while time.time() - start_time < max_wait:
            if self.scanner_status != "Scanning":
                break
            time.sleep(0.1)

        if self.scanner_status != "Done" or self.devices == []:
            self.logger.info("Scanner not found any devices")
            return False

        available_devices = self.list_devices()
        if len(self.devices) > 1 and chosen_device is None:
            self.logger.info(
                "Multiple devices or connection found, selecting the first one"
            )

        if self.selected_device is None:
            if not chosen_device:
                device_order = 0
            else:
                # If a specific device is chosen, find its index
                device_order = next(
                    (
                        i
                        for i, d in enumerate(self.devices)
                        if d.DeviceId == chosen_device
                    ),
                    0,
                )
            self.select_device(self.devices[device_order].DeviceId)

        if self.streaming_formats_supported == []:
            self.get_streaming_formats()

        return True

    def auto_connect(
        self,
        selected_format=None,
        force_scan=False,
        reconnect=False,
        chosen_device=None,
    ):
        self.fetch_resources(
            selected_format=selected_format,
            force_scan=force_scan,
            reconnect=reconnect,
            chosen_device=chosen_device,
        )

        if self.streaming_format is None:
            selected_format = "Dual" if not selected_format else selected_format
            self.set_streaming_format(selected_format)

        if not self._camera.is_connected:
            authenticated = False
            self.connect_to_camera(authenticated=authenticated)

        max_wait = 60  # seconds
        start_time = time.time()
        while time.time() - start_time < max_wait:
            if self._camera.is_connected:
                if self._camera.is_image_initialized:
                    break
            time.sleep(1)

        return True

    def start_scanning(self):
        """
        Start scanning for available camera devices.
        This should be async
        """
        try:
            self.scanner.Start(
                live.Discovery.Interface.Default
                # | live.Discovery.Interface.Network
                # | live.Discovery.Interface.Bluetooth
                # | live.Discovery.Interface.Usb
                # | live.Discovery.Interface.Usb3
                # | live.Discovery.Interface.Gigabit
                # | live.Discovery.Interface.Firewire
                # | live.Discovery.Interface.Spinnaker
            )
            self.logger.info("Started scanning for devices")
            self.scanner_status = "Scanning"
        except Exception as e:
            self.logger.error(f"Failed to start scanner: {str(e)}")

    def stop_scanning(self):
        """
        Stop scanning for available camera devices.
        """
        self.scanner.Stop()
        self.scanner_status = "stopped"
        self.logger.info("Stopped scanning for devices")

    def on_device_found(self, sender, e: live.Discovery.CameraDiscoveredEventArgs):
        """
        Handle the event when a device is found.

        Args:
            sender: The sender of the event.
            e: The event arguments containing the discovered device.
        """
        if e.Device not in self.devices:
            self.devices.append(e.Device)
        self.logger.info(f"Device found: {e.Device.Name}")
        self.scanner_status = "Done"
        # ws.publish() #TODO: Send devices found on ws

    def on_device_lost(self, sender, e: live.Discovery.CameraLostEventArgs):
        """
        Handle the event when a device is lost.

        Args:
            sender: The sender of the event.
            e: The event arguments containing the lost device.
        """
        self.devices = [
            device for device in self.devices if device.DeviceId != e.Device.DeviceId
        ]
        self.logger.info(f"Device lost: {e.Device.Name}")
        # ws.publish() #TODO: Send devices lost on ws

    def on_device_error(self, sender, e: live.Device.DeviceErrorEventArgs):
        self.logger.error(f"{e}")

    def list_devices(self):
        """
        List the discovered devices.

        Returns:
            A list of dictionaries containing the name and ID of each device.
        """
        devices = []

        # TODO: handle device if is CameraDeviceInfo or Network Camera
        for device in self.devices:

            device_info = self.scanner.Resolve(device)

            device_dict = {
                "name": device_info.Name,
                "serial": device_info.SerialNumber,
                "id": device.DeviceId,
                "devide_name": device.Name,
                "interface": device.Interface,
                "device_info": device_info,
            }

            devices.append(device_dict)

        self.devices_list = devices

        if not devices:
            self.logger.info("No devices found")
            return []

        self.logger.info("Listed devices")

        devices = [
            {
                "name": f"{device.get('name')} - {device.get('serial')}",
                "id": device.get("id"),
            }
            for device in devices
        ]

        return devices

    def select_device(self, device_id):
        """
        Select a device from the discovered devices.

        Args:
            device_id: The ID of the device to select.

        Returns:
            True if the device was found and selected, False otherwise.
        """
        self.selected_device = next(
            (device for device in self.devices if device.DeviceId == device_id), None
        )
        if self.selected_device:

            self._camera.camera_device_info = self.scanner.Resolve(
                self.selected_device
            )  # device_identifier

            self.logger.info(f"Selected device: {self.selected_device.Name}")
            return True
        else:
            self.logger.info(f"Device not found: {device_id}")
            return False

    def get_streaming_formats(self):
        """
        Get the available streaming formats for the selected device.

        Returns:
            A list of available streaming formats.
        """
        try:
            if self.selected_device:
                self.logger.info(
                    f"Retrieved streaming formats for device: {self.selected_device.Name}"
                )
                # TODO: finish
                # security_parameters = live.Device.CameraBase.SecurityParameters()

                formats_obj = self._camera.camera_device_info.StreamingFormats

                format_labels = {"Argb": "Visual", "FlirFileFormat": "Radiométrico"}

                format_priority = {"FlirFileFormat": 0, "Dual": 2, "Argb": 1}

                formats = [
                    {
                        "index": i,
                        "name": fmt.ToString(),
                        "label": format_labels.get(fmt.ToString(), fmt.ToString()),
                    }
                    for i, fmt in enumerate(formats_obj)
                ]

                formats.sort(key=lambda x: format_priority.get(x["name"], float("inf")))

                self.streaming_formats_supported = formats

                return [i["label"] for i in formats]

        except AttributeError as e:
            self.logger.error(f"Error retrieving streaming formats: {str(e)}")
            return []

    def set_streaming_format(self, format):
        """
        Set the streaming format for the selected device.

        Args:
            format: The streaming format to set.
        """
        try:
            if self.selected_device:
                format_dict = next(
                    (
                        fmt
                        for fmt in self.streaming_formats_supported
                        if fmt["label"] == format
                    ),
                    None,
                )

                format_obj = next(
                    (
                        fmt
                        for fmt in self._camera.camera_device_info.StreamingFormats
                        if fmt.ToString() == format_dict["name"]
                    ),
                    None,
                )

                if format_obj:
                    self.streaming_format = format_obj
                    self.streaming_format_name = format_dict["name"]
                    # TODO: Fix selection
                    self._camera.camera_device_info.SelectedStreamingFormat = format_obj
                    self.logger.info(
                        f"Set streaming format to '{format}' for device: {self.selected_device.Name}"
                    )
                else:
                    raise
        except Exception as e:
            self.logger.error(f"Erro ao selecionar formato: {str(e)}")

    def connect_to_camera(self, authenticated=False, reconnect=False):
        """
        Connect to the selected camera device.

        Args:
            authenticated: Whether to use authentication.
            reconnect: Whether to reconnect to the camera.

        Returns:
            True if the connection was successful, False otherwise.
        """

        # if not self.selected_device:
        # try:
        #     with self._camera.camera_lock:
        #         # self.disconnect()
        with self._camera.camera_lock:
            try:
                # self.disconnect()

                security_parameters = (
                    live.Security.SecurityParameters() if authenticated else None
                )

                # TODO: Implement resolve if ip address from camera connected by network
                status = live.Discovery.ThermalCameraScanner.Resolve(
                    self.selected_device,  # device
                    security_parameters,  # securityParameters
                    self._camera.camera_device_info,  # deviceInfo
                )

                # TODO: Check if shoud stop the function
                if status != live.Security.AuthenticationStatus.Approved:
                    self.logger.info(f"Resposta de autenticação: {status}")
                    # return False
                if self._camera.camera_device_info is None:
                    self.logger.info("Não foi possível resolver a câmera")
                    # return False

                # Select the appropriate camera type based on the streaming format
                # streaming_format = (
                #     self._camera.camera_device_info.SelectedStreamingFormat
                # )
                streaming_format = self.streaming_format

                if streaming_format == live.Discovery.ImageFormat.FlirFileFormat:
                    self._camera.camera = live.Device.ThermalCamera()
                    self._camera.is_thermal_image_supported = True
                    self._camera.is_visual_image_supported = False

                elif streaming_format == live.Discovery.ImageFormat.Argb:
                    self._camera.camera = live.Device.VideoOverlayCamera()
                    self._camera.is_thermal_image_supported = False
                    self._camera.is_visual_image_supported = True

                elif streaming_format == live.Discovery.ImageFormat.Dual:
                    self._camera.is_thermal_image_supported = True
                    self._camera.is_visual_image_supported = True

                    # TODO: Implement this properly. Receive the format from the front end
                    dual_format = (
                        live.Device.DualStreamingFormat.Fusion
                        if self.streaming_format_name in ["Fusion", "Dual"]
                        else live.Device.DualStreamingFormat.Dual  # TODO: Test this format
                    )

                    self._camera.camera = live.Device.DualStreamingThermalCamera(
                        True, dual_format
                    )

                    self._camera.is_dual_streaming = isinstance(
                        self._camera.camera, live.Device.DualStreamingThermalCamera
                    )

                else:
                    self.logger.critical(
                        f"Formato de câmera não suportado: {streaming_format}",
                    )
                    return False

                if not reconnect:
                    try:
                        # Attach specific event handlers using event manager
                        self._camera.camera.DeviceError += (
                            self._camera.event_manager.on_device_error
                        )

                        self._camera.camera.ConnectionStatusChanged += (
                            self._camera.event_manager.on_connection_status_changed
                        )
                        self._camera.camera.ImageReceived += (
                            self._camera.event_manager.on_image_received
                        )
                        self._camera.camera.ImageInitialized += (
                            self._camera.event_manager.on_image_initialized
                        )

                        # Setup generic event capture for all other events
                        self._camera.event_manager.setup_generic_event_capture()

                    except Exception as e:
                        self.logger.error(f"Error defining event handlers - {e}")

                try:
                    # Connect to the camera
                    self._camera.camera.Connect(
                        self._camera.camera_device_info, security_parameters
                    )

                    # Wait until the camera is connected
                    max_wait_time = 30  # Maximum wait time in seconds
                    wait_interval = 0.1  # Interval between checks in seconds
                    elapsed_time = 0

                    while (
                        not self._camera.camera.IsConnected
                        and elapsed_time < max_wait_time
                    ):
                        time.sleep(wait_interval)
                        elapsed_time += wait_interval

                    if not self._camera.camera.IsConnected:
                        self.logger.info(
                            "Erro ao conectar com a camera: Tempo de espera excedido",
                        )
                        return False

                    self._camera.is_connected = self._camera.camera.IsConnected
                    self.is_connection_established = True

                except Exception as e:
                    self.logger.error(f"Erro ao conectar com a camera: {str(e)}")

                if not self._camera.camera.IsGrabbing:
                    try:
                        self._camera.camera.StartGrabbing()  # Inicia a captura de imagens
                        self.logger.info("Start grabbing images manually")
                    except Exception as e:
                        self.logger.error(
                            f"Erro ao iniciar a captura de imagens: {str(e)}"
                        )

                try:
                    # Set the camera control
                    self._camera.camera_control.set_camera(self._camera.camera)

                except Exception as e:
                    self.logger.error(f"Error setting controls - {e}")

                self.logger.info(
                    f"Conectado à câmera: {self._camera.camera_device_info.Name}"
                )

            except Exception as e:
                self.logger.error(f"Erro na conexão com a câmera: {str(e)}")

                return False

            # while live.Device.GrabberState != 3:
            #     self.logger.info(live.Device.GrabberState)
            #     pass

            image = None
            try:
                image = self._camera.extract_image()
            except Exception as e:
                self.logger.error(f"Error generating first image - {e}")

            if image is not None:
                self._camera.palette_name = self.get_palette()
                self._camera.event_manager.on_image_initialized(self, None)
                self._camera.event_manager.on_image_received(
                    self, type("obj", (object,), {"Image": image})()
                )

            # Inicia monitoramento de hardware após conexão bem sucedida
            # self._start_heartbeat()

            # self.fill_camera_info()
            self.logger.info("Connection finalized")
            return True

    def reconnect(self):
        """
        Attempt to reconnect to the camera if the connection is lost.
        """
        if self.selected_device:
            self._camera.camera.Connect(
                self.selected_device, self._camera.security_parameters
            )

    def disconnect(self, reconnect=False):
        """
        Disconnect from the currently connected camera.
        """
        # Para o monitoramento de hardware
        self._stop_heartbeat_monitor()

        # Stop the UI refresh loop
        self._camera.connection_status = "Disconnected"

        if self._camera.camera is not None:
            if not reconnect:
                try:
                    # Use event manager's cleanup to remove all handlers
                    self._camera.event_manager.cleanup()
                except Exception as e:
                    self.logger.error(f"Error cleaning up event handlers: {e}")

            # Stop grabbing images and disconnect the camera
            self._camera.camera.StopGrabbing()
            self._camera.camera.Disconnect()
            self._camera.camera.Dispose()
            self._camera.camera = None

            self._camera.is_connected = False
            self.is_connection_established = False

            self.logger.info("Disconnected from camera")

            # Update UI elements
            # self._camera.update_ui_on_disconnect()

    def fill_camera_info(self):
        """
        Fill the camera information.

        Returns:
            A dictionary containing the camera information.
        """

        self.logger.info("start collection information")
        if self._camera.camera is not None:

            self._camera.fps = self._camera.camera.Fps

            self._camera.camera_model = (
                self._camera.image_obj_thermal.CameraInformation.Model
            )
            self._camera.camera_serial_number = (
                self._camera.image_obj_thermal.CameraInformation.SerialNumber
            )
            self._camera.camera_lens = (
                self._camera.image_obj_thermal.CameraInformation.Lens
            )
            self._camera.camera_fov = (
                self._camera.image_obj_thermal.CameraInformation.Fov
            )
            self._camera.camera_range = (
                self._camera.image_obj_thermal.CameraInformation.Range
            )
            self._camera.camera_filter = (
                self._camera.image_obj_thermal.CameraInformation.Filter
            )

            self._camera.camera_name = self._camera.camera_device_info.Name
            self._camera.camera_ip = self._camera.camera_device_info.IpSettings
            self._camera.camera_serial = self._camera.camera_device_info.SerialNumber
            self._camera.camera_article = self._camera.camera_device_info.Article
            self._camera.camera_device_identifier = (
                self._camera.camera_device_info.DeviceIdentifier
            )
            self._camera.camera_streaming_format_name = (
                self._camera.camera_device_info.StreamingFormatName
            )

            self._camera.width = self._camera.image_obj_thermal.Width
            self._camera.height = self._camera.image_obj_thermal.Height

            # self._camera.palette = self._camera.camera_device_info.Port
            # self._camera.palette_name = self._camera.camera_device_info.Port

        return None

    def get_palette(self):
        """
        Get the current palette of the camera.

        Returns:
            The current palette of the camera.
        """
        if self._camera.camera is not None:
            try:
                return self._camera.camera.RemoteControl.CameraSettings.GetPaletteName()
            except Exception as e:
                self.logger.error(f"Error getting palette: {str(e)}")

        return None
