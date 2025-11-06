"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

import datetime
import json
import os
from threading import Lock
from typing import Any, Dict, Optional

import clr

from config.settings import settings
from utils import object_handler
from utils.LoggerConfig import LoggerConfig

logger = LoggerConfig.add_file_logger(
    name="image_data_service", filename=None, dir_name=None, prefix="image_service"
)

# Add the path to the directory containing the compiled DLL
dll_path = os.path.join(settings.BASE_DIR, "ThermalCameraLibrary")

clr.AddReference(os.path.join(dll_path, "ThermalCamera.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Live.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Image.dll"))
clr.AddReference("System")

import Flir.Atlas.Image as Image  # type: ignore

# Import the necessary classes from the assembly
import Flir.Atlas.Live as live  # type: ignore

from camera.image.measurements.measurements import CameraMeasurements
from camera.image.resources.camera_info import CameraInfo
from camera.image.resources.compass_info import CompassInfo
from camera.image.resources.gas_quantification import GasQuantification

# Import resource classes
from camera.image.resources.gps_info import GPSInfo
from camera.image.resources.image_metadata import ImageMetadata
from camera.image.resources.statistics_info import StatisticsInfo
from camera.image.resources.thermal_parameters import ThermalParameters
from camera.image.resources.zoom_info import ZoomInfo
from camera.palettes.palettes import PaletteHandler


class ImageDataService:
    """
    Service class to extract and provide thermal image data through various resource classes.
    This service can work with either a connected camera or a provided thermal image.
    """

    def __init__(self, camera=None):
        """
        Initialize the ImageDataService.

        Args:
            camera: Optional camera instance. If provided, will extract data from camera's current image.
        """
        self._camera = camera
        self.logger = logger
        self._service_lock = Lock() if camera is None else camera.service_lock

        # Initialize resource classes
        if self._camera:
            self.gps_info = GPSInfo(self._camera)
            self.compass_info = CompassInfo(self._camera)
            self.camera_info = CameraInfo(self._camera)
            self.thermal_parameters = ThermalParameters(self._camera)
            self.gas_quantification = GasQuantification(self._camera)
            self.zoom_info = ZoomInfo(self._camera)
            self.statistics_info = StatisticsInfo(self._camera)
            self.image_metadata = ImageMetadata(self._camera)
            self.palette_handler = PaletteHandler(self._camera)

        else:
            # Initialize with None camera - will need thermal_image parameter for data extraction
            self.gps_info = None
            self.compass_info = None
            self.camera_info = None
            self.thermal_parameters = None
            self.gas_quantification = None
            self.zoom_info = None
            self.statistics_info = None
            self.image_metadata = None
            self.palette_handler = None

    def update_all_data(
        self, thermal_image: Optional[Any] = None, camera: Optional[Any] = None
    ) -> None:
        """
        Update all thermal image data from the provided thermal image or camera's current image.

        Args:
            thermal_image: Optional thermal image object. If None, uses camera's current imag
        """
        with self._service_lock:
            try:
                # Determine the thermal image to use
                image_to_use = (
                    thermal_image
                    if thermal_image
                    else (
                        camera.image_obj_thermal
                        if camera
                        else self._camera.image_obj_thermal
                    )
                )

                if image_to_use is None:
                    self.logger.warning(
                        "No thermal image available for data extraction"
                    )
                    return

                # Initialize resources if not already done (for standalone usage)
                if self.image_metadata is None:
                    self._initialize_standalone_resources(
                        thermal_image=image_to_use, camera=self._camera
                    )

                resources_map = self.get_resources_map(get_all=True)

                # Update all resource data
                for resource in resources_map:
                    if resource["is_supported"]:
                        resource["object"].update_info(image_to_use)

                # self.logger.info("Successfully updated all thermal image data")

            except Exception as e:
                self.logger.error(f"Error updating thermal image data: {e}")

    def _initialize_standalone_resources(
        self, thermal_image: Any, camera: Optional[Any] = None
    ) -> None:
        """
        Initialize resource classes for standalone usage (without camera instance).

        Args:
            thermal_image: Thermal image object
        """

        if settings.MOCK_CAMERA:
            # If mock camera is used, create a mock camera object
            _camera = type(
                "MockCamera",
                (),
                {
                    "logger": self.logger,
                    "image_obj_thermal": thermal_image,
                    "image_obj_visual": None,
                    "service_lock": Lock(),
                    "fps": None,
                    "camera": None,
                },
            )()
        else:
            # Otherwise, use the provided thermal image directly
            _camera = thermal_image if not camera else camera

        self.gps_info = GPSInfo(_camera)
        self.compass_info = CompassInfo(_camera)
        self.camera_info = CameraInfo(_camera)
        self.thermal_parameters = ThermalParameters(_camera)
        self.gas_quantification = GasQuantification(_camera)
        self.zoom_info = ZoomInfo(_camera)
        self.statistics_info = StatisticsInfo(_camera)
        self.image_metadata = ImageMetadata(_camera)
        self.palette_handler = PaletteHandler(_camera)

        # Sensors
        # Alarms
        # Isotherms
        # Measurements
        # Histogram
        # TriggerData
        # Fusion
        # Pipeline
        # Scale

    def get_complete_data_dict(
        self, thermal_image: Optional[Any] = None, camera: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Get complete thermal image data as a dictionary.

        Args:
            thermal_image: Optional thermal image object

        Returns:
            Dictionary containing all thermal image data
        """
        # Update data first
        self.update_all_data(thermal_image, camera)

        complete_data = {}

        resources_map = self.get_resources_map(get_all=True)

        for resource in resources_map:
            complete_data[resource["external_name"]] = (
                self._get_resource_with_support_status(resource["object"])
            )

        # complete_data = {
        #     "ImageMetaData": self._get_resource_with_support_status(
        #         self.image_metadata
        #     ),
        #     "CameraInformation": self._get_resource_with_support_status(
        #         self.camera_info
        #     ),
        #     "CompassInformation": self._get_resource_with_support_status(
        #         self.compass_info
        #     ),
        #     "GasQuantification": self._get_resource_with_support_status(
        #         self.gas_quantification
        #     ),
        #     "GpsInformation": self._get_resource_with_support_status(self.gps_info),
        #     "ThermalParameters": self._get_resource_with_support_status(
        #         self.thermal_parameters
        #     ),
        #     "Statistics": self._get_resource_with_support_status(self.statistics_info),
        #     "ZoomInformation": self._get_resource_with_support_status(self.zoom_info),
        #     "Palette": self._get_resource_with_support_status(self.palette_handler),
        #     "Sensors": {"is_supported": False},  # TODO
        #     "Alarms": {"is_supported": False},  # TODO
        #     "Isotherms": {"is_supported": False},  # TODO
        #     "Measurements": {"is_supported": False},  # TODO
        #     "Histogram": {"is_supported": False},  # TODO
        #     "TriggerData": {"is_supported": False},  # TODO
        #     "Fusion": {"is_supported": False},  # TODO
        #     "Pipeline": {"is_supported": False},  # TODO
        #     "Scale": {"is_supported": False},  # TODO
        # }

        return complete_data

    def get_complete_data_json(self, thermal_image: Optional[Any] = None) -> str:
        """
        Get complete thermal image data as a JSON string.

        Args:
            thermal_image: Optional thermal image object

        Returns:
            JSON string containing all thermal image data
        """
        data_dict = self.get_complete_data_dict(thermal_image)
        return json.dumps(data_dict, indent=2, default=str)

    def get_specific_data(
        self, data_type: str, thermal_image: Optional[Any] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get specific type of thermal image data.

        Args:
            data_type: Type of data to retrieve ('gps', 'compass', 'camera', 'thermal_params','gas', 'zoom', 'statistics', 'metadata', 'palette')
            thermal_image: Optional thermal image object

        Returns:
            Dictionary containing specific data type or None if not found
        """
        # self.update_all_data(thermal_image)
        resource_map = self.get_resources_map(data_type=data_type)
        data_map = {}

        for resource in resource_map:
            if resource.get("is_supported", True):
                resource["object"].update_info(thermal_image)
                data_map[resource["external_name"]] = (
                    self._get_resource_with_support_status(resource["object"])
                )
            else:
                data_map[resource["external_name"]] = {"is_supported": False}

        return data_map

    def _get_resource_with_support_status(self, resource) -> Dict[str, Any]:
        """
        Get resource data with support status information.

        Args:
            resource: The resource object to process

        Returns:
            Dict containing resource data with is_supported flag
        """
        if resource is None:
            return {"is_supported": False}

        # Get the resource data using to_dict
        resource_data = self.to_dict(self, resource)

        # Check if the resource data is empty or None
        if not resource_data or resource_data is None:
            return {"is_supported": False}

        # Check if all values in the resource data are None or empty
        all_empty = True
        for value in resource_data.values():
            if value is not None and value != "" and value != {} and value != []:
                all_empty = False
                break

        if all_empty:
            return {"is_supported": False}

        # If we reach here, the resource is supported
        resource_data["is_supported"] = True
        return resource_data

    def get_resources_map(
        self, data_type: str = None, get_all: bool = False
    ) -> list[dict]:
        """
        Parse the data type to a valid format.
        """
        data_map = [
            {
                "internal_name": "image_metadata",
                "external_name": "ImageMetaData",
                "is_supported": self.image_metadata.is_supported,
                "object": self.image_metadata,
            },
            {
                "internal_name": "camera_info",
                "external_name": "CameraInformation",
                "is_supported": self.camera_info.is_supported,
                "object": self.camera_info,
            },
            {
                "internal_name": "compass_info",
                "external_name": "CompassInformation",
                "is_supported": self.compass_info.is_supported,
                "object": self.compass_info,
            },
            {
                "internal_name": "gas_quantification",
                "external_name": "GasQuantification",
                "is_supported": self.gas_quantification.is_supported,
                "object": self.gas_quantification,
            },
            {
                "internal_name": "gps_info",
                "external_name": "GpsInformation",
                "is_supported": self.gps_info.is_supported,
                "object": self.gps_info,
            },
            {
                "internal_name": "thermal_params",
                "external_name": "ThermalParameters",
                "is_supported": self.thermal_parameters.is_supported,
                "object": self.thermal_parameters,
            },
            {
                "internal_name": "statistics_info",
                "external_name": "Statistics",
                "is_supported": self.statistics_info.is_supported,
                "object": self.statistics_info,
            },
            {
                "internal_name": "zoom_info",
                "external_name": "ZoomInformation",
                "is_supported": self.zoom_info.is_supported,
                "object": self.zoom_info,
            },
            {
                "internal_name": "palette",
                "external_name": "Palette",
                "is_supported": self.palette_handler.is_supported,
                "object": self.palette_handler,
            },
            {
                "internal_name": "measurements",
                "external_name": "Measurements",
                "is_supported": False,
                "object": None,
            },
            {
                "internal_name": "alarms",
                "external_name": "Alarms",
                "is_supported": False,
                "object": None,
            },
            {
                "internal_name": "isotherms",
                "external_name": "Isotherms",
                "is_supported": False,
                "object": None,
            },
            {
                "internal_name": "sensors",
                "external_name": "Sensors",
                "is_supported": False,
                "object": None,
            },
            {
                "internal_name": "histogram",
                "external_name": "Histogram",
                "is_supported": False,
                "object": None,
            },
            {
                "internal_name": "trigger_data",
                "external_name": "TriggerData",
                "is_supported": False,
                "object": None,
            },
            {
                "internal_name": "fusion",
                "external_name": "Fusion",
                "is_supported": False,
                "object": None,
            },
            {
                "internal_name": "pipeline",
                "external_name": "Pipeline",
                "is_supported": False,
                "object": None,
            },
            {
                "internal_name": "scale",
                "external_name": "Scale",
                "is_supported": False,
                "object": None,
            },
        ]

        # logger.debug(f"Parsing data type: {data_type}")
        if get_all:
            return data_map

        resource_map = [
            i
            for i in data_map
            if i["external_name"] == data_type or i["internal_name"] == data_type
        ]
        if len(resource_map) == 0:
            return None

        return resource_map

    @staticmethod
    def to_dict(self, resource) -> dict:
        json_response = {}
        try:
            if resource.__class__.__name__ == "CameraInfo":
                json_response = {
                    "Model": ImageDataService.serialize_resource_attr(
                        "Model", resource
                    )["Model"],
                    "SerialNumber": ImageDataService.serialize_resource_attr(
                        "SerialNumber", resource
                    )["SerialNumber"],
                    "Lens": ImageDataService.serialize_resource_attr("Lens", resource)[
                        "Lens"
                    ],
                    "Filter": ImageDataService.serialize_resource_attr(
                        "Filter", resource
                    )["Filter"],
                    "Fov": ImageDataService.serialize_resource_attr("Fov", resource)[
                        "Fov"
                    ],
                    "Range": ImageDataService.serialize_resource_attr(
                        "Range", resource
                    )["Range"],
                    "Fps": ImageDataService.serialize_resource_attr("Fps", resource)[
                        "Fps"
                    ],
                    "AveragePayload": ImageDataService.serialize_resource_attr(
                        "AveragePayload", resource
                    )["AveragePayload"],
                    "FrameCount": ImageDataService.serialize_resource_attr(
                        "FrameCount", resource
                    )["FrameCount"],
                    "FrameRateIndex": ImageDataService.serialize_resource_attr(
                        "FrameRateIndex", resource
                    )["FrameRateIndex"],
                    "LostImages": ImageDataService.serialize_resource_attr(
                        "LostImages", resource
                    )["LostImages"],
                    "TimelapseReconnect": ImageDataService.serialize_resource_attr(
                        "TimelapseReconnect", resource
                    )["TimelapseReconnect"],
                    "TimeoutCheckForHeartbeat": ImageDataService.serialize_resource_attr(
                        "TimeoutCheckForHeartbeat", resource
                    )[
                        "TimeoutCheckForHeartbeat"
                    ],
                }
            elif resource.__class__.__name__ == "GPSInfo":
                json_response = {
                    "IsValid": ImageDataService.serialize_resource_attr(
                        "IsValid", resource
                    )["IsValid"],
                    "Altitude": ImageDataService.serialize_resource_attr(
                        "Altitude", resource
                    )["Altitude"],
                    "AltitudeRef": ImageDataService.serialize_resource_attr(
                        "AltitudeRef", resource
                    )["AltitudeRef"],
                    "Dop": ImageDataService.serialize_resource_attr("Dop", resource)[
                        "Dop"
                    ],
                    "Latitude": ImageDataService.serialize_resource_attr(
                        "Latitude", resource
                    )["Latitude"],
                    "LatitudeRef": ImageDataService.serialize_resource_attr(
                        "LatitudeRef", resource
                    )["LatitudeRef"],
                    "Longitude": ImageDataService.serialize_resource_attr(
                        "Longitude", resource
                    )["Longitude"],
                    "LongitudeRef": ImageDataService.serialize_resource_attr(
                        "LongitudeRef", resource
                    )["LongitudeRef"],
                    "MapDatum": ImageDataService.serialize_resource_attr(
                        "MapDatum", resource
                    )["MapDatum"],
                    "Satellites": ImageDataService.serialize_resource_attr(
                        "Satellites", resource
                    )["Satellites"],
                    "Timestamp": ImageDataService.serialize_resource_attr(
                        "Timestamp", resource
                    )["Timestamp"],
                }
            elif resource.__class__.__name__ == "CompassInfo":
                json_response = {
                    "Degrees": ImageDataService.serialize_resource_attr(
                        "Degrees", resource
                    )["Degrees"],
                    "Roll": ImageDataService.serialize_resource_attr("Roll", resource)[
                        "Roll"
                    ],
                    "Pitch": ImageDataService.serialize_resource_attr(
                        "Pitch", resource
                    )["Pitch"],
                }
            elif resource.__class__.__name__ == "ThermalParameters":
                json_response = {
                    "AtmosphericTemperature": ImageDataService.serialize_resource_attr(
                        "AtmosphericTemperature", resource
                    )["AtmosphericTemperature"],
                    "Distance": ImageDataService.serialize_resource_attr(
                        "Distance", resource
                    )["Distance"],
                    "Emissivity": ImageDataService.serialize_resource_attr(
                        "Emissivity", resource
                    )["Emissivity"],
                    "ExternalOpticsTemperature": ImageDataService.serialize_resource_attr(
                        "ExternalOpticsTemperature", resource
                    )[
                        "ExternalOpticsTemperature"
                    ],
                    "ExternalOpticsTransmission": ImageDataService.serialize_resource_attr(
                        "ExternalOpticsTransmission", resource
                    )[
                        "ExternalOpticsTransmission"
                    ],
                    "ReferenceTemperature": ImageDataService.serialize_resource_attr(
                        "ReferenceTemperature", resource
                    )["ReferenceTemperature"],
                    "ReflectedTemperature": ImageDataService.serialize_resource_attr(
                        "ReflectedTemperature", resource
                    )["ReflectedTemperature"],
                    "RelativeHumidity": ImageDataService.serialize_resource_attr(
                        "RelativeHumidity", resource
                    )["RelativeHumidity"],
                    "Transmission": ImageDataService.serialize_resource_attr(
                        "Transmission", resource
                    )["Transmission"],
                }
            elif resource.__class__.__name__ == "GasQuantification":
                json_response = {
                    "Result": {
                        "Flow": ImageDataService.serialize_resource_attr(
                            "Flow", resource
                        )["Flow"],
                        "Concentration": ImageDataService.serialize_resource_attr(
                            "Concentration", resource
                        )["Concentration"],
                    },
                    "Input": {
                        "IsValid": ImageDataService.serialize_resource_attr(
                            "IsValid", resource
                        )["IsValid"],
                        "AmbientTemperature": ImageDataService.serialize_resource_attr(
                            "AmbientTemperature", resource
                        )["AmbientTemperature"],
                        "Gas": ImageDataService.serialize_resource_attr(
                            "Gas", resource
                        )["Gas"],
                        "LeakType": ImageDataService.serialize_resource_attr(
                            "LeakType", resource
                        )["LeakType"],
                        "WindSpeed": ImageDataService.serialize_resource_attr(
                            "WindSpeed", resource
                        )["WindSpeed"],
                        "Distance": ImageDataService.serialize_resource_attr(
                            "Distance", resource
                        )["Distance"],
                        "ThresholdDeltaTemperature": ImageDataService.serialize_resource_attr(
                            "ThresholdDeltaTemperature", resource
                        )[
                            "ThresholdDeltaTemperature"
                        ],
                        "Emissive": ImageDataService.serialize_resource_attr(
                            "Emissive", resource
                        )["Emissive"],
                    },
                }
            elif resource.__class__.__name__ == "StatisticsInfo":
                json_response = {
                    "Min": ImageDataService.serialize_resource_attr("Min", resource)[
                        "Min"
                    ],
                    "Max": ImageDataService.serialize_resource_attr("Max", resource)[
                        "Max"
                    ],
                    "Average": ImageDataService.serialize_resource_attr(
                        "Average", resource
                    )["Average"],
                    "StandardDeviation": ImageDataService.serialize_resource_attr(
                        "StandardDeviation", resource
                    )["StandardDeviation"],
                    "ColdSpot": ImageDataService.serialize_resource_attr(
                        "ColdSpot", resource
                    )["ColdSpot"],
                    "HotSpot": ImageDataService.serialize_resource_attr(
                        "HotSpot", resource
                    )["HotSpot"],
                }
            elif resource.__class__.__name__ == "ZoomInfo":
                json_response = {
                    "Factor": ImageDataService.serialize_resource_attr(
                        "Factor", resource
                    )["Factor"],
                    "PanX": ImageDataService.serialize_resource_attr("PanX", resource)[
                        "PanX"
                    ],
                    "PanY": ImageDataService.serialize_resource_attr("PanY", resource)[
                        "PanY"
                    ],
                }
            elif resource.__class__.__name__ == "ImageMetadata":
                json_response = {
                    "FileName": ImageDataService.serialize_resource_attr(
                        "FileName", resource
                    )["FileName"],
                    "Height": ImageDataService.serialize_resource_attr(
                        "Height", resource
                    )["Height"],
                    "Width": ImageDataService.serialize_resource_attr(
                        "Width", resource
                    )["Width"],
                    "FrameCount": ImageDataService.serialize_resource_attr(
                        "FrameCount", resource
                    )["FrameCount"],
                    "TemperatureUnit": ImageDataService.serialize_resource_attr(
                        "TemperatureUnit", resource
                    )["TemperatureUnit"],
                    "DistanceUnit": ImageDataService.serialize_resource_attr(
                        "DistanceUnit", resource
                    )["DistanceUnit"],
                    "ColorDistribution": ImageDataService.serialize_resource_attr(
                        "ColorDistribution", resource
                    )["ColorDistribution"],
                    "Description": ImageDataService.serialize_resource_attr(
                        "Description", resource
                    )["Description"],
                    "DateTime": ImageDataService.serialize_resource_attr(
                        "DateTime", resource
                    )["DateTime"],
                    "DateTaken": ImageDataService.serialize_resource_attr(
                        "DateTaken", resource
                    )["DateTaken"],
                    "ContainsUltraMaxData": ImageDataService.serialize_resource_attr(
                        "ContainsUltraMaxData", resource
                    )["ContainsUltraMaxData"],
                    "MaxSignalValue": ImageDataService.serialize_resource_attr(
                        "MaxSignalValue", resource
                    )["MaxSignalValue"],
                    "MinSignalValue": ImageDataService.serialize_resource_attr(
                        "MinSignalValue", resource
                    )["MinSignalValue"],
                    "OverflowSignalValue": ImageDataService.serialize_resource_attr(
                        "OverflowSignalValue", resource
                    )["OverflowSignalValue"],
                    "UnderflowSignalValue": ImageDataService.serialize_resource_attr(
                        "UnderflowSignalValue", resource
                    )["UnderflowSignalValue"],
                    "Precision": ImageDataService.serialize_resource_attr(
                        "Precision", resource
                    )["Precision"],
                    "isLiveStream": True if self._camera else False,
                }
            elif resource.__class__.__name__ == "PaletteHandler":
                json_response = {
                    "available_palettes": ImageDataService.serialize_resource_attr(
                        "available_palettes", resource
                    )["available_palettes"],
                    "current_palette": {
                        "name": ImageDataService.serialize_resource_attr(
                            "name", resource
                        )["name"],
                        "is_inverted": ImageDataService.serialize_resource_attr(
                            "is_inverted", resource
                        )["is_inverted"],
                        "underflow_color": ImageDataService.serialize_resource_attr(
                            "underflow_color", resource
                        )["underflow_color"],
                        "overflow_color": ImageDataService.serialize_resource_attr(
                            "overflow_color", resource
                        )["overflow_color"],
                        "below_span_color": ImageDataService.serialize_resource_attr(
                            "below_span_color", resource
                        )["below_span_color"],
                        "above_span_color": ImageDataService.serialize_resource_attr(
                            "above_span_color", resource
                        )["above_span_color"],
                        "version": ImageDataService.serialize_resource_attr(
                            "palette_version", resource
                        )["palette_version"],
                    },
                }
        except Exception as e:
            logger.error(f"Error serializing {resource.__class__.__name__}: {e}")
        return json_response

    @staticmethod
    def serialize_resource_attr(attr_name: str, resource: Any) -> dict:
        """
        Serializes a single attribute from a resource object.

        Args:
            attr_name (str): The name of the attribute to serialize
            resource (Any): The resource object

        Returns:
            dict: Dictionary with the attribute name and its serialized value
        """
        try:
            value = getattr(resource, attr_name, None)
            serialized = object_handler.serialize_object(value)
            return {attr_name: serialized}
        except Exception as e:
            logger.error(
                f"Error serializing attribute '{attr_name}' from {type(resource).__name__}: {e}"
            )
            return {attr_name: None, "error": str(e)}
