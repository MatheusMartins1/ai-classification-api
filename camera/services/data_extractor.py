"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

import os
from typing import Any, Dict, Optional, Union

import clr

from config.settings import settings
from utils import object_handler
from utils.infrastructure import get_local_ip
from utils.LoggerConfig import LoggerConfig

logger = LoggerConfig.add_file_logger(
    name="image_data_extractor",
    filename=None,
    dir_name=None,
    prefix="data_extractor",
    level_name="ERROR",
)

from camera.image.image_service import ImageDataService

# Add the path to the directory containing the compiled DLL
DLL_PATH = os.path.join(settings.BASE_DIR, "ThermalCameraLibrary")

clr.AddReference(os.path.join(DLL_PATH, "ThermalCamera.dll"))
clr.AddReference(os.path.join(DLL_PATH, "Flir.Atlas.Live.dll"))
clr.AddReference(os.path.join(DLL_PATH, "Flir.Atlas.Image.dll"))
clr.AddReference("System")

import Flir.Atlas.Image as Image  # type: ignore


class DataExtractorService:
    """
    Simple service to extract thermal data for the main views.
    Focuses only on data extraction without creating additional endpoints or Redis publishers.
    """

    _service = None

    @staticmethod
    def extract_thermal_data(
        thermal_image, data_to_extract: str = "complete", camera: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Extract thermal data based on the requested data type.

        Args:
            thermal_image: Thermal image object from camera
            data_to_extract: Type of data to extract
                - "complete" or None: All available data
                - "gps": GPS information only
                - "camera": Camera information only
                - "thermal_params": Thermal parameters only
                - "gas": Gas quantification data only
                - "compass": Compass information only
                - "zoom": Zoom information only
                - "statistics": Statistics information only
                - "metadata": Image metadata only
                - "palette": "Palette information (available palettes, current palette, colors, etc.)",

                #TODO: Add more data types
                "Sensors": "#TODO",
                "Alarms": "#TODO",
                "Isotherms": "#TODO",
                "Measurements": "#TODO",
                "Histogram": "#TODO",
                "TriggerData": "#TODO",
                "Fusion": "#TODO",
                "Pipeline": "#TODO",
                "Scale": "#TODO",

        Returns:
            Dictionary containing requested thermal data
        """
        try:
            # Normalize data_to_extract
            if data_to_extract.lower().strip() == "complete":
                return DataExtractorService._extract_complete_data(
                    thermal_image, camera
                )
            else:
                return DataExtractorService._extract_specific_data(
                    thermal_image, data_to_extract, camera
                )

        except Exception as e:
            logger.error(f"Error extracting thermal data: {e}")
            return {
                "error": f"Failed to extract thermal data: {str(e)}",
                "requested_data_type": data_to_extract,
                "available_types": [
                    "complete",
                    "gps",
                    "camera",
                    "thermal_params",
                    "gas",
                    "compass",
                    "zoom",
                    "statistics",
                    "metadata",
                    "palette",
                ],
            }

    @staticmethod
    def _extract_complete_data(
        thermal_image, camera: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Extract all available thermal data.

        Args:
            thermal_image: Thermal image object

        Returns:
            Dictionary containing all thermal data
        """
        try:
            if DataExtractorService._service is None:
                # Use the service to get complete data
                if camera is None:
                    service = ImageDataService()
                else:
                    service = ImageDataService(camera)

                DataExtractorService._service = service

            complete_data = DataExtractorService._service.get_complete_data_dict(
                thermal_image, camera
            )

            logger.info("Successfully extracted complete thermal data")
            return complete_data

        except Exception as e:
            logger.error(f"Error extracting complete thermal data: {e}")
            raise e

    @staticmethod
    def _extract_specific_data(
        thermal_image, data_type: str, camera: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Extract specific type of thermal data.

        Args:
            thermal_image: Thermal image object
            data_type: Type of data to extract

        Returns:
            Dictionary containing specific thermal data
        """
        try:
            if DataExtractorService._service is None:
                if camera is None:
                    service = ImageDataService()
                else:
                    service = ImageDataService(camera)

                DataExtractorService._service = service

            specific_data = DataExtractorService._service.get_specific_data(
                data_type, thermal_image
            )

            if specific_data is None:
                return {
                    "error": f"No data available for type: {data_type}",
                    "requested_type": data_type,
                }

            logger.info(f"Successfully extracted {data_type} thermal data")
            return {"data_type": data_type, "data": specific_data}

        except Exception as e:
            logger.error(f"Error extracting {data_type} thermal data: {e}")
            return {
                "error": f"Failed to extract {data_type} data: {str(e)}",
                "requested_type": data_type,
            }

    @staticmethod
    def get_available_data_types() -> Dict[str, str]:
        """
        Get available data types and their descriptions.

        Returns:
            Dictionary mapping data types to descriptions
        """
        return {
            "complete": "All available thermal data",
            "gps": "GPS coordinates and location information",
            "camera": "Camera model, serial number, and technical specifications",
            "thermal_params": "Thermal measurement parameters (emissivity, distance, etc.)",
            "gas": "Gas detection and quantification data",
            "compass": "Compass and orientation information (degrees, roll, pitch)",
            "zoom": "Zoom level and optical information",
            "statistics": "Statistical data (min, max, average, standard deviation)",
            "metadata": "Basic image metadata (dimensions, units, timestamps)",
            "palette": "Palette information (name, colors, etc.)",
        }

    @staticmethod
    def validate_data_type(data_type: str) -> tuple[bool, str]:
        """
        Validate if the requested data type is supported.

        Args:
            data_type: Data type to validate

        Returns:
            Tuple of (is_valid, message)
        """
        available_types = DataExtractorService.get_available_data_types()
        normalized_type = (data_type or "complete").lower().strip()

        if normalized_type in available_types:
            return True, f"Valid data type: {available_types[normalized_type]}"

        return (
            False,
            f"Invalid data type '{data_type}'. Available types: {list(available_types.keys())}",
        )

    @staticmethod
    def format_response_for_view(
        thermal_data: Dict[str, Any], data_type: str = "complete"
    ) -> Dict[str, Any]:
        """
        Format thermal data response for view consumption.

        Args:
            thermal_data: Extracted thermal data
            data_type: Type of data that was requested

        Returns:
            Formatted response dictionary
        """
        try:
            # Check if there was an error in extraction
            if "error" in thermal_data:
                return {
                    "status": False,
                    "message": thermal_data["error"],
                    "imageData": None,
                    "requested_type": data_type,
                }

            # Format successful response
            return {
                "status": True,
                "message": f"Thermal data extracted successfully ({data_type})",
                "imageData": thermal_data,
                "requested_type": data_type,
                "data_keys": (
                    list(thermal_data.keys())
                    if isinstance(thermal_data, dict)
                    else None
                ),
            }

        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            return {
                "status": False,
                "message": f"Error formatting response: {str(e)}",
                "imageData": None,
                "requested_type": data_type,
            }

    @staticmethod
    def get_mock_cameras_info(
        detail_level: str = "full", selected_format: str = "Dual"
    ) -> list[dict]:
        """
        Generate a list of mock camera information with the same structure as get_camera_info.

        Args:
            detail_level (str): Level of detail to include - 'basic', 'full', or 'minimal'
            selected_format (str): Format to use for the camera

        Returns:
            list[dict]: List of mock camera information dictionaries
        """
        cameras: list[dict] = []

        # Example: create 2 mock cameras for demonstration
        for idx in range(2):
            camera_info = {
                "id": f"mock_camera_{idx+1}",
                "name": f"Gx620-{idx+1}",
                "serialNumber": f"123789{idx+1}",
                "connectionStatus": "Connected",
                "isConnected": True,
                "isNucSupported": True,
                "isFocusSupported": True,
                "isHsmSupported": True,
                "isDualFovSupported": True,
                "isRecorderSupported": True,
                "isSnapshotSupported": True,
            }

            # Basic level adds common fields
            if detail_level in ["basic", "full"]:
                camera_info.update(
                    {
                        "ipAddress": get_local_ip(),
                        "isDualStreaming": False,
                        "isThermalImageSupported": True,
                        "isVisualImageSupported": True,
                        "streamFormatSelected": "webcam",
                        "streamFormat": "webcam",
                    }
                )

            # Full detail includes everything
            if detail_level == "full":
                camera_info.update(
                    {
                        "scannerDevice": None,
                        "streamFormatSupported": ["webcam"],
                        "article": "Mock Article",
                        "lens": "FOL23",
                        "fov": 24.002296447753906,
                        "range": "Mock Range",
                        "fps": 30,
                        "width": 640,
                        "height": 480,
                    }
                )

            cameras.append(camera_info)

        return cameras

    @staticmethod
    def get_camera_info(
        camera, detail_level: str = "full", selected_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate standardized camera information.

        Args:
            camera: Optional camera instance. If None, gets the singleton instance.
            detail_level: Level of detail to include - 'basic', 'full', or 'minimal'
            selected_format: Override the camera's selected format if needed

        Returns:
            dict: Standardized camera information dictionary
        """
        try:
            camera.connection_manager.fill_camera_info()
            # Base camera info available in all detail levels
            camera_info = {
                "id": camera.camera_device_identifier,
                "name": camera.camera_name,
                "serialNumber": camera.camera_serial,
                "connectionStatus": camera.connection_status,
                "isConnected": camera.is_connected,
                "isNucSupported": camera.camera_control.is_nuc_supported,
                "isFocusSupported": camera.camera_control.is_focus_supported,
                "isHsmSupported": camera.camera_control.is_hsm_supported,
                "isDualFovSupported": camera.camera_control.is_dual_fov_supported,
                "isRecorderSupported": camera.camera_control.is_recorder_supported,
                "isSnapshotSupported": camera.camera_control.is_snapshot_supported,
            }

            # Basic level adds common fields needed for most operations
            if detail_level in ["basic", "full"]:
                camera_info.update(
                    {
                        "ipAddress": (
                            camera.camera_ip.IpAddress if camera.camera_ip else None
                        ),
                        "isDualStreaming": camera.is_dual_streaming,
                        "isThermalImageSupported": camera.is_thermal_image_supported,
                        "isVisualImageSupported": camera.is_visual_image_supported,
                        "streamFormat": camera.connection_manager.streaming_format_name,
                        "streamFormatSelected": camera.connection_manager.streaming_format_name,
                    }
                )

            # Full detail includes everything
            if detail_level == "full":
                camera_info.update(
                    {
                        "scannerDevice": [
                            {"name": device.Name, "id": device.DeviceId}
                            for device in camera.connection_manager.devices
                        ],
                        "streamFormatSupported": camera.connection_manager.streaming_formats_supported,
                        "article": camera.camera_article,
                        "lens": camera.camera_lens,
                        "fov": camera.camera_fov,
                        "range": (
                            {}
                            if not camera.camera_range
                            else {
                                "min": camera.camera_range.Minimum,
                                "max": camera.camera_range.Maximum,
                            }
                        ),
                        "fps": (
                            int(camera.camera.Fps)
                            if camera.camera.Fps
                            else int(camera.fps) if camera.fps else 0
                        ),
                        "width": camera.width,
                        "height": camera.height,
                    }
                )

            return camera_info

        except Exception as e:
            logger.error(f"Error generating camera info: {str(e)}")

            # Return minimal info on error
            return {
                "error": str(e),
                "isConnected": (
                    False
                    if not hasattr(camera, "is_connected")
                    else camera.is_connected
                ),
                "connectionStatus": (
                    "Error"
                    if not hasattr(camera, "connection_status")
                    else camera.connection_status
                ),
            }

    @staticmethod
    def get_thermal_data_for_view(
        camera=None, data_to_extract: str = "complete"
    ) -> Dict[str, Any]:
        """
        Convenience function to get thermal data formatted for view response.

        Args:
            thermal_image: Thermal image object
            data_to_extract: Type of data to extract

        Returns:
            Formatted response dictionary ready for JsonResponse
        """

        if settings.MOCK_CAMERA and camera:
            file_path = r"C:\projects\tenesso\image_subtraction"
            img_name = "FLIR1511.jpg"
            img_name = "FLIR0139.jpg"
            # img_name = "IR_26-05-2023_0006.jpg" #Com compasso
            # img_name = "FLIR0089.jpg" #Com gasleak

            image_path = os.path.join(file_path, img_name)
            thermal_image = Image.ThermalImageFile(image_path)
        else:
            thermal_image = camera.image_obj_thermal

        thermal_data = DataExtractorService.extract_thermal_data(
            thermal_image, data_to_extract, camera=camera
        )

        view_response = DataExtractorService.format_response_for_view(
            thermal_data, data_to_extract
        )

        return view_response

    @staticmethod
    def validate_thermal_data_request(data_to_extract: str) -> tuple[bool, str]:
        """
        Convenience function to validate thermal data requests.

        Args:
            data_to_extract: Data type to validate

        Returns:
            Tuple of (is_valid, message)
        """
        return DataExtractorService.validate_data_type(data_to_extract)
