"""
Developer: Matheus Martins da Silva
Creation Date: 10/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva.
"""

import datetime
import os
import time
from io import BytesIO
from typing import Any, Optional

import clr
import numpy as np
from PIL import Image as PILImage

from config.settings import settings

# Add references to DLLs
dll_path = os.path.join(settings.BASE_DIR, "ThermalCameraLibrary")
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Live.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Image.dll"))
clr.AddReference("System")

import Flir.Atlas.Image as Image  # type: ignore

# Import Flir SDK
import Flir.Atlas.Live as live  # type: ignore

# Import local modules
import image.bitmap_handler as bitmap_handler
import System  # type: ignore

from utils.LoggerConfig import LoggerConfig
from utils.Polling import PollingManager, PollingResult

logger = LoggerConfig.add_file_logger(
    name="image_extraction", filename=None, dir_name=None, prefix="camera"
)

polling_manager = PollingManager()


class ImageExtractor:
    """
    Handles image extraction and conversion from Flir camera.
    Single responsibility: Extract and convert camera images to numpy arrays.
    """

    def __init__(self, camera_manager: Any) -> None:
        """
        Initialize the image extractor.

        Args:
            camera_manager: Reference to the CameraManager instance
        """
        self._camera = camera_manager
        self.logger = logger

    def validate_extraction_ready(self, max_wait: float = 10.0) -> bool:
        """
        Validate if camera is ready for image extraction with polling and thread-safe checks.

        Args:
            max_wait: Maximum time to wait in seconds for camera to be ready

        Returns:
            bool: True if camera is ready for extraction, False otherwise
        """
        if not self._camera.camera:
            self.logger.error("Camera not initialized")
            return False

        # Check 1: Camera connection with thread safety
        with self._camera._locks("control"):
            try:
                if not self._camera.camera.IsConnected:
                    self.logger.error("Camera not connected")
                    return False
            except Exception as e:
                self.logger.error(f"Error checking camera connection: {e}")
                return False

        # Check 2: Images marked as ready
        with self._camera._locks("control"):
            if not self._camera.is_image_ready:
                self.logger.warning("Images not marked as ready yet")
                # Try waiting for images to be ready
                if not self._camera.wait_for_image_ready(timeout=max_wait):
                    self.logger.error("Timeout waiting for images to be ready")
                    return False

        # Check 3: Grabber state with polling
        def check_grabber_ready() -> bool:
            """Check if grabber is ready"""
            with self._camera._locks("control"):
                try:
                    grabber_state = self._camera.camera.IsGrabberReady
                    if grabber_state == live.Device.GrabberState.Ready:
                        self.logger.debug("Grabber is ready")
                        return True
                    else:
                        self.logger.debug(f"Grabber not ready - state: {grabber_state}")
                        return False
                except AttributeError:
                    self.logger.error("IsGrabberReady attribute not available")
                    return False
                except Exception as e:
                    self.logger.error(f"Error checking grabber state: {e}")
                    return False

        poll_result = polling_manager.poll_until_condition(
            condition_func=check_grabber_ready,
            interval=0.5,
            max_wait=max_wait,
            error_handler=lambda e: self.logger.error(f"Polling error: {e}") or False,
        )

        if poll_result == PollingResult.TIMEOUT:
            self.logger.error(
                f"Timeout waiting for grabber to be ready after {max_wait}s"
            )
            return False
        elif poll_result == PollingResult.ERROR:
            self.logger.error("Error during grabber state polling")
            return False

        # Check 4: Camera is grabbing images
        with self._camera._locks("control"):
            try:
                if not self._camera.camera.IsGrabbing:
                    self.logger.error("Camera is not grabbing images")
                    return False
            except AttributeError:
                self.logger.warning("IsGrabbing attribute not available")
            except Exception as e:
                self.logger.error(f"Error checking IsGrabbing: {e}")
                return False

        # Check 5: Required attributes exist based on camera type
        with self._camera._locks("control"):
            has_required_attrs = False

            if self._camera.is_thermal_image_supported:
                try:
                    has_required_attrs = hasattr(self._camera.camera, "ThermalImage")
                    if not has_required_attrs:
                        self.logger.error("ThermalImage attribute not available")
                except Exception as e:
                    self.logger.error(f"Error checking ThermalImage attribute: {e}")

            if self._camera.is_visual_image_supported:
                try:
                    has_visual = hasattr(self._camera.camera, "Visual")
                    has_required_attrs = has_required_attrs or has_visual
                    if not has_visual and not has_required_attrs:
                        self.logger.error("Visual attribute not available")
                except Exception as e:
                    self.logger.error(f"Error checking Visual attribute: {e}")

            if not has_required_attrs:
                self.logger.error("No required image attributes available")
                return False

        self.logger.info("Camera validation passed - ready for extraction")
        return True

    def get_image_objects(
        self, validate: bool = True
    ) -> tuple[Optional[Any], Optional[Any]]:
        """
        Safely get thermal and visual image objects from camera.

        Args:
            validate: If True, validates camera state before extraction

        Returns:
            Tuple of (thermal_image_obj, visual_image_obj), either can be None
        """
        thermal_obj = None
        visual_obj = None

        if not self._camera.camera:
            self.logger.error("Camera not initialized")
            return (None, None)

        # Validate camera is ready for extraction
        if validate:
            if not self.validate_extraction_ready():
                self.logger.error("Camera validation failed - cannot extract images")
                return (None, None)

        # Get thermal image object
        if self._camera.is_thermal_image_supported:
            try:
                thermal_obj = self._camera.camera.ThermalImage
                if thermal_obj:
                    self.logger.info("Thermal image object acquired")
            except System.AccessViolationException:
                self.logger.error(
                    "Access violation getting thermal image object - camera busy"
                )
            except AttributeError:
                self.logger.debug("ThermalImage not available on this camera type")
            except Exception as e:
                self.logger.warning(f"Could not get thermal image object: {e}")

        # Get visual image object
        if self._camera.is_visual_image_supported:
            try:
                visual_obj = self._camera.camera.Visual
                if visual_obj:
                    self.logger.info("Visual image object acquired")
            except System.AccessViolationException:
                self.logger.error(
                    "Access violation getting visual image object - camera busy"
                )
            except AttributeError:
                self.logger.debug("Visual not available on this camera type")
            except Exception as e:
                self.logger.warning(f"Could not get visual image object: {e}")

        return (thermal_obj, visual_obj)

    def extract_image(self, image: Optional[Any] = None) -> Optional[np.ndarray]:
        """
        Get the current image from the camera.

        Args:
            image: Optional pre-loaded image object

        Returns:
            The current image from the camera as a numpy array, or None if extraction fails
        """
        if self._camera.camera is None:
            self.logger.info("Camera is not connected")
            return None

        if not self._camera.check_image_ready():
            self.logger.warning("Images not ready for extraction yet")
            if not self._camera.wait_for_image_ready(timeout=5.0):
                self.logger.error("Timeout waiting for images to be ready")
                return None

        image_base_visual = None
        image_base_thermal = None
        image_visual_np = None
        image_thermal_np = None

        # TODO: Add Fusion Image and Gigevision
        if not image:
            if self._camera.is_visual_image_supported:
                try:
                    if self._camera.is_dual_streaming:
                        image_base_visual = self._camera.camera.Visual
                    else:
                        image_base_visual = self._camera.camera.VisualImage

                    self._camera.image_type = str(image_base_visual)
                except System.AccessViolationException:
                    self.logger.error(
                        "Access violation getting visual image - camera busy"
                    )
                    return None
                except Exception as e:
                    self.logger.error(f"Error getting visual image object - {e}")

            if self._camera.is_thermal_image_supported:
                try:
                    if self._camera.is_dual_streaming:
                        image_base_thermal = self._camera.camera.Thermal
                    else:
                        image_base_thermal = self._camera.camera.GetImage()

                    self._camera.image_type = str(image_base_thermal)
                except System.AccessViolationException:
                    self.logger.error(
                        "Access violation getting thermal image - camera busy"
                    )
                    return None
                except Exception as e:
                    self.logger.error(f"Error getting thermal image object - {e}")

        support_visual_image = (
            image_base_visual and self._camera.is_visual_image_supported
        ) or self._camera.is_dual_streaming

        # Process visual image - get_image() handles its own .NET locks
        if support_visual_image:
            try:
                image_bitmap_visual = self.get_image(
                    image_base=image_base_visual, img_type="bitmap"
                )
                image_visual_np = self.convert_image_to_numpy(image=image_bitmap_visual)

                self._camera.image_obj_visual = image_base_visual
                self._camera.image_bitmap_visual = image_bitmap_visual

                self._camera.current_visual_image = image_visual_np
                self._camera.current_visual_image_resized = (
                    self._camera.image_processor.process_image(
                        image_visual_np, resize=self._camera.resize_image
                    )
                )

            except Exception as ex:
                self.logger.error(f"Erro ao processar a imagem visual: {str(ex)}")

        # Process thermal image - get_image() handles its own .NET locks
        if image_base_thermal is not None:
            try:
                image_bitmap_thermal = self.get_image(
                    image_base=image_base_thermal, img_type="bitmap"
                )
                image_thermal_np = self.convert_image_to_numpy(
                    image=image_bitmap_thermal
                )

                self._camera.image_obj_thermal = image_base_thermal
                self._camera.image_bitmap_thermal = image_bitmap_thermal

                self._camera.current_thermal_image = image_thermal_np
                self._camera.current_thermal_image_resized = (
                    self._camera.image_processor.process_image(
                        image_thermal_np, resize=self._camera.resize_image
                    )
                )

            except Exception as ex:
                self.logger.error(f"Erro ao processar a imagem termal: {str(ex)}")

        try:
            self._camera.image_list.append(
                {
                    "thermal_image": image_thermal_np,
                    "visual_image": image_thermal_np,
                    "thermal_image_resized": self._camera.current_thermal_image_resized,
                    "visual_image_resized": self._camera.current_visual_image_resized,
                }
            )
        except Exception as e:
            self.logger.error(f"Erro ao setar controles - {e}")

        if image_thermal_np is not None:
            return image_thermal_np
        if image_visual_np is not None:
            return image_visual_np

        return None

    def get_image(self, image_base: Any, img_type: str = "array") -> Optional[Any]:
        """
        Attempt to get the image from the imageBase with retries.

        Args:
            image_base: The base image object from which to get the image
            img_type: The type of image to retrieve ("array" or "bitmap")

        Returns:
            The image if successful, None otherwise
        """
        max_retries = 10
        wait_interval = 0.1
        retries = 0
        image = None

        # TODO: Add Gigevision and Fusion Image
        # TODO: Add ImageReady, GrabberState and others that my block access to the image

        # Use TryEnterLock() for non-blocking lock acquisition
        # More efficient than EnterLock() as it integrates with retry logic
        has_lock_support = hasattr(image_base, "TryEnterLock") and hasattr(
            image_base, "ExitLock"
        )

        while retries < max_retries:
            lock_acquired = False

            try:
                # Try to acquire .NET lock (non-blocking)
                if has_lock_support:
                    lock_acquired = image_base.TryEnterLock()

                    if not lock_acquired:
                        self.logger.debug(
                            f"Could not acquire lock, retry {retries + 1}/{max_retries}"
                        )
                        retries += 1
                        time.sleep(wait_interval)
                        continue

                # Lock acquired or not needed, try to get image
                try:
                    if img_type == "bitmap":
                        image = image_base.Image
                    elif img_type == "array":
                        image = image_base.ImageArray()
                    else:
                        raise ValueError("Image type not found")

                    if image is not None:
                        break

                except System.AccessViolationException:
                    self.logger.error(
                        "Access violation - camera busy (NUC/calibration)"
                    )
                    break
                except Exception as ex:
                    self.logger.debug(f"Error accessing image property: {str(ex)}")

            except Exception as ex:
                self.logger.error(f"Erro ao resgatar a imagem: {str(ex)}")

            finally:
                # Always release .NET lock if it was acquired
                if lock_acquired:
                    try:
                        image_base.ExitLock()
                    except Exception as ex:
                        self.logger.error(f"Error releasing image lock: {str(ex)}")

            retries += 1
            if image is None:
                self.logger.debug(
                    f"Image not available, waiting {wait_interval}s - retry {retries}/{max_retries}"
                )
                time.sleep(wait_interval)

        if image is not None:
            return image

        self.logger.error("Falha ao obter a imagem após várias tentativas")
        return None

    def convert_image_to_numpy(self, image: Any) -> Optional[np.ndarray]:
        """
        Convert the FLIR image to a numpy array.

        Args:
            image: The FLIR image object

        Returns:
            The image as a numpy array, or None if conversion fails
        """
        if not image:
            return None

        elif isinstance(image, System.Drawing.Bitmap):
            try:
                # Converta para OpenCV (ARGB vira BGRA, RGB vira BGR)
                cv2_image = bitmap_handler.bitmap_to_cv2(image)

                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(
                    settings.BASE_DIR,
                    "static_media",
                    "snapshots",
                    f"img_{timestamp}.jpg",
                )
                # cv2.imwrite(filename, cv2_image, [cv2.IMWRITE_JPEG_QUALITY, 90])

                return cv2_image
            except Exception as e:
                self.logger.error(e)
                return None

        elif (
            isinstance(image, System.Array)
            and image.GetType().GetElementType() == System.Byte
        ):
            # Converter System.Byte[] para PIL Image
            byte_array = bytearray(image)
            pil_image = PILImage.open(BytesIO(byte_array))

            # Converter PIL Image para array NumPy
            return np.array(pil_image)

        elif isinstance(image, Image.ThermalImage):
            # Convert ThermalImage to numpy array
            return np.array(image.Image)

        elif isinstance(image, Image.VisualImage):
            # Convert VisualImage to numpy array
            return np.array(image.Image)

        elif (
            isinstance(image, System.Array)
            and image.Rank == 3
            and image.GetType().GetElementType() == clr.GetClrType(System.Byte)
        ):
            # Caso 3: Byte[,,] (array 3D do .NET)
            try:
                # Converter System.Array[Byte] para NumPy
                # Nota: O array .NET tem dimensões [height, width, channels]
                height = image.GetLength(0)
                width = image.GetLength(1)
                channels = image.GetLength(2)

                # Cria um buffer 1D para copiar os bytes
                buffer = bytearray(height * width * channels)
                System.Buffer.BlockCopy(image, 0, buffer, 0, len(buffer))

                # Converte para array NumPy 3D (uint8)
                np_array = np.frombuffer(buffer, dtype=np.uint8).reshape(
                    (height, width, channels)
                )

                # # OpenCV espera BGR (se o array for RGB)
                # if channels == 3:
                #     np_array = cv2.cvtColor(np_array, cv2.COLOR_RGB2BGR)
                # elif channels == 4:
                #     np_array = cv2.cvtColor(np_array, cv2.COLOR_RGBA2BGRA)

                return np_array

            except Exception as e:
                self.logger.error(e)
                return None
        else:
            raise ValueError("Unsupported image type")
