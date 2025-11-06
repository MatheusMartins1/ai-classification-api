"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

import os
from threading import Lock
from typing import Any, Dict, List, Optional

import clr

from config.settings import settings
from utils import object_handler

# Add the path to the directory containing the compiled DLL
dll_path = os.path.join(settings.BASE_DIR, "ThermalCameraLibrary")

clr.AddReference(os.path.join(dll_path, "ThermalCamera.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Live.dll"))
clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Image.dll"))
clr.AddReference("System")

# clr.AddReference(os.path.join(dll_path, "Flir.Atlas.Gigevision.dll"))
import tempfile

import Flir.Atlas.Image as Image  # type: ignore

# Import the necessary classes from the assembly
import Flir.Atlas.Live as live  # type: ignore

# WebSocket/Message Broker
from camera._delete.events import EventBus as ws
from camera.image.measurements.measurement_shape import MeasurementShapeManager


class CameraMeasurements:
    """
    A class to represent the CameraMeasurements from Flir's Atlas SDK.

    Reference:
        https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/namespace_flir_1_1_atlas_1_1_image_1_1_measurements.html
    """

    def __init__(self, _camera):
        """
        Initialize the CameraMeasurements class with a FlirAlarm instance.

        """
        self._camera = _camera
        self.logger = _camera.logger
        self._service_lock = _camera.service_lock
        self.is_supported = True

        self._image = _camera.image_obj_thermal

        self._measurements = {"measurements": []}

        self.measurement_shape_handler = MeasurementShapeManager(_camera)

        # TEST: THIS
        self._image_file = self.convert_image_to_image_file(self._image)

        self._check_if_supported(self._image)

        self.initialize()

    def _check_if_supported(self, thermal_image: Optional[Any] = None):
        """
        Check if the measurements are supported by the camera.
        """
        if thermal_image is None and self._image is None:
            self.is_supported = False
            return

        try:
            if thermal_image.Measurements is None:
                self.is_supported = False
                return
        except Exception as e:
            self.is_supported = False
            return

    def initialize(self) -> None:
        """Initialize existing measurements from the camera."""
        if not self._camera.is_thermal_image_supported:
            return

        if not self._image:
            return

        try:
            measurements_enum = self._image.Measurements.GetEnumerator()
            measurement_count = (
                0
                if not self._image.Measurements.Count
                else self._image.Measurements.Count
            )

            if measurements_enum and measurement_count > 0:
                index = 0
                while measurements_enum.MoveNext():
                    current_measurement = measurements_enum.Current
                    measurement_dict = self._build_measurements_dict(
                        measurement=current_measurement
                    )

                    self._measurements["measurements"].append(measurement_dict)
                    index += 1

                self.logger.info(
                    f"Initialized {len(self._measurements['measurements'])} measurements"
                )
        except Exception as e:
            self.logger.error(f"Error initializing measurements: {e}")

    def update_info(self, thermal_image: Optional[Any] = None):
        """
        Update the measurements information from the thermal image.
        """
        if thermal_image is None and self._image is None:
            return

        thermal_image = (
            thermal_image
            if isinstance(thermal_image, Image.ThermalImage)
            else self._image
        )

        self._check_if_supported(thermal_image)

        measurements = self.get_all_measurements(rasterize=True)

        # Extract measurements values
        for measurement in measurements:
            measurement_dict = self._build_measurements_dict(measurement)

    def clear_all(self) -> bool:
        """Clear all measurements using MeasurementShapeCollection.Clear method."""
        try:
            self._image.Measurements.Clear()
            self._measurements["measurements"].clear()

            self.logger.info("Cleared all measurements and measurement shapes.")
            # ws.publish(event="measurements_cleared", data=self._measurements)
            return True
        except Exception as e:
            self.logger.error(f"Error clearing measurements: {e}")
            return False

    def add_measurement(
        self, measurement_type: str, config: dict, operation_type: str = "create"
    ) -> Optional[Dict]:
        """
        Add or update a measurement using MeasurementShapeCollection.Add method.

        Args:
            measurement_type (str): Type of measurement to create/update
            config (dict): Configuration dictionary for the measurement
            operation_type (str): "create" for new measurement, "update" for existing

        Returns:
            Optional[Dict]: Measurement dictionary if successful, None otherwise
        """
        try:
            # Validate measurement type
            if measurement_type not in [
                "rectangle",
                "spot",
                "line",
                "ellipse",
                "delta",
            ]:
                raise ValueError(f"Invalid measurement type: {measurement_type}")

            # Validate config based on type
            self._validate_measurement_config(measurement_type, config)

            # Use the new create_or_update methods based on operation type
            if measurement_type == "rectangle":
                measurement = self.measurement_shape_handler.create_or_update_rectangle(
                    config, operation_type
                )
            elif measurement_type == "spot":
                measurement = self.measurement_shape_handler.create_or_update_spot(
                    config, operation_type
                )
            elif measurement_type == "line":
                measurement = self.measurement_shape_handler.create_or_update_line(
                    config, operation_type
                )
            elif measurement_type == "ellipse":
                measurement = self.measurement_shape_handler.create_or_update_ellipse(
                    config, operation_type
                )
            # if measurement_type == "delta":
            #     shape = self.measurement_shape_handler.create_delta(measurement_type,config)

            if not measurement:
                return None

            # Set name if provided
            if config.get("name"):
                measurement.Name = config.get("name")

            # Build measurement dictionary
            measurement_dict = self._build_measurements_dict(
                measurement=measurement,
                measurement_config=config,
                measurement_type=measurement_type,
            )

            # For create operations, add to measurements list
            if operation_type == "create":
                self._measurements["measurements"].append(measurement_dict)
                self.logger.info(
                    f"Added {measurement_type} measurement: {measurement_dict.get('id')}"
                )
            else:
                # For update operations, update existing measurement in list
                self._update_measurement_in_list(measurement_dict)
                self.logger.info(
                    f"Updated {measurement_type} measurement: {measurement_dict.get('id')}"
                )

            return measurement_dict

        except Exception as e:
            self.logger.error(f"Error {operation_type}ing measurement: {e}")
            return None

    def _update_measurement_in_list(self, updated_measurement: Dict[str, Any]) -> None:
        """
        Update an existing measurement in the internal measurements list.

        Args:
            updated_measurement (Dict[str, Any]): Updated measurement dictionary
        """
        try:
            measurement_id = updated_measurement.get("id")
            if not measurement_id:
                return

            # Find and update existing measurement in list
            for i, measurement in enumerate(self._measurements["measurements"]):
                if measurement.get("id") == measurement_id:
                    self._measurements["measurements"][i] = updated_measurement
                    break
        except Exception as e:
            self.logger.error(f"Error updating measurement in list: {e}")

    def get_all_measurements(self, rasterize: bool = True) -> List[Dict]:
        """
        Get all measurements.

        Args:
            rasterize (bool): Whether to serialize the measurements

        Returns:
            List of dictionaries containing measurement information
        """
        if not self._camera.is_thermal_image_supported:
            return []

        try:
            if rasterize:
                measurements = [
                    object_handler.serialize_object(i)
                    for i in self._measurements["measurements"]
                ]
                return measurements
            else:
                return self._measurements["measurements"]
        except Exception as e:
            self.logger.error(f"Error getting all measurements: {e}")
            return []

    def get_measurement(self, measurement_id: str) -> Optional[Dict]:
        """
        Get measurement by ID.

        Args:
            measurement_id: Unique identifier of the measurement

        Returns:
            Dictionary containing measurement information or None if not found
        """
        try:
            for measurement in self._measurements["measurements"]:
                if measurement["id"] == measurement_id:
                    return measurement
            return None
        except Exception as e:
            self.logger.error(f"Error getting measurement: {e}")
            return None

    def update_measurement(self, measurement_id: str, config: dict) -> bool:
        """Update measurement using the new unified add_measurement method."""
        try:
            # Get measurement type from existing measurement
            measurement_dict = self.get_measurement(measurement_id)
            if not measurement_dict:
                return False

            measurement_type = measurement_dict.get("type")
            if not measurement_type:
                self.logger.error(
                    f"Measurement type not found for ID: {measurement_id}"
                )
                return False

            # Add measurement_id to config for update operation
            # config["id"] = measurement_id

            # Use add_measurement with update operation type
            # result = self.measurement_shape_handler.add_measurement(
            #     measurement_type=measurement_type,
            #     config=config,
            #     operation_type="update"
            # )

            # Use the new create_or_update methods based on operation type
            if measurement_type == "rectangle":
                measurement = self.measurement_shape_handler.create_or_update_rectangle(
                    config, operation_type="update"
                )
            elif measurement_type == "spot":
                measurement = self.measurement_shape_handler.create_or_update_spot(
                    config, operation_type="update"
                )
            elif measurement_type == "line":
                measurement = self.measurement_shape_handler.create_or_update_line(
                    config, operation_type="update"
                )
            elif measurement_type == "ellipse":
                measurement = self.measurement_shape_handler.create_or_update_ellipse(
                    config, operation_type="update"
                )
            # if measurement_type == "delta":
            #     shape = self.measurement_shape_handler.create_delta(measurement_type,config)

            updated_measurement_dict = self._build_measurements_dict(
                measurement=measurement,
                measurement_config=config,
                measurement_type=measurement_type,
                measurement_index=measurement_dict.get("index"),
            )

            # For update operations, update existing measurement in list
            self._update_measurement_in_list(updated_measurement_dict)
            self.logger.info(
                f"Updated {measurement_type} measurement: {updated_measurement_dict.get('id')}"
            )
            return measurement

        except Exception as e:
            self.logger.error(f"Error updating measurement: {e}")
            return False

    def delete_measurement(self, measurement_id: str) -> bool:
        """
        Delete measurement by ID.

        Args:
            measurement_id: Unique identifier of the measurement

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            for i, measurement in enumerate(self._measurements["measurements"]):
                if measurement["id"] == measurement_id:
                    self._image.Measurements.Remove(measurement["measurement"])
                    self._measurements["measurements"].pop(i)
                    self.logger.info(f"Deleted measurement: {measurement_id}")
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting measurement: {e}")
            return False

    def remove_measurement(self, measurement_id: str) -> bool:
        """Remove measurement using MeasurementShapeCollection.Remove method."""
        try:
            for i, measurement in enumerate(self._measurements["measurements"]):
                if measurement["id"] == measurement_id:
                    # Remove from collection
                    self._image.Measurements.Remove(measurement["measurement"])
                    # Remove from local cache
                    self._measurements["measurements"].pop(i)
                    self.logger.info(f"Removed measurement: {measurement_id}")
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Error removing measurement: {e}")
            return False

    def _validate_measurement_config(self, measurement_type: str, config: dict) -> None:
        """Validate measurement configuration parameters."""
        required_fields = {
            "rectangle": ["x", "y", "width", "height"],
            "ellipse": ["x", "y", "width", "height"],
            "spot": ["x", "y"],
            "line": ["x1", "y1", "x2", "y2"],
            # "polyline":[""],
            # "polygon": [""],
            "delta": ["points"],
        }

        fields = required_fields.get(measurement_type, [])
        missing = [f for f in fields if f not in config]

        if missing:
            raise ValueError(
                f"Missing required fields for {measurement_type}: {', '.join(missing)}"
            )

    def convert_image_to_image_file(self, image):
        """
        Convert the image to an image file.
        """
        if not image:
            return None

        if not hasattr(image, "SaveSnapshot"):
            return None

        # Salva a imagem em um arquivo temporário
        temp_file_path = os.path.join(tempfile.gettempdir(), "temp_image.fff")
        os.makedirs(tempfile.gettempdir(), exist_ok=True)

        try:
            image.SaveSnapshot(temp_file_path)
        except Exception as e:
            self.logger.error(f"Erro ao salvar a imagem temporária: {e}")
            return None

        try:
            thermal_image_file = Image.ThermalImageFile(temp_file_path)
            self.logger.debug("Imagem convertida para ThermalImageFile.")
            return thermal_image_file
        except Exception as e:
            self.logger.error(f"Falha ao converter imagem para ThermalImageFile: {e}")

        # Tenta criar uma instância de VisualImageFile
        try:
            visual_image_file = Image.VisualImageFile(temp_file_path)
            self.logger.debug("Imagem convertida para VisualImageFile.")
            return visual_image_file
        except Exception as e:
            self.logger.error(f"Falha ao converter imagem para VisualImageFile: {e}")

        return None

    def _check_measurements_exists(self, measurement: Any) -> bool:
        """
        Check if measurement exists in the collection.

        Args:
            measurement: The measurement object to check

        Returns:
            bool: True if measurement exists, False otherwise
        """
        try:
            return self._image.Measurements.Contains(measurement)
        except Exception as e:
            self.logger.error(f"Error checking if measurement exists: {str(e)}")
            return False

    def _get_measurements_index(self, measurement: Any) -> Optional[int]:
        """
        Get the index of a measurement in the collection. If measurement doesn't exist,
        return the next available index based on collection count.

        Args:
            measurement: The measurement object to find the index for

        Returns:
            Optional[int]: The index of the measurement if found or next available index, None if error
        """
        try:
            measurement_exists = self._check_measurements_exists(measurement)
            index = None

            if measurement_exists:
                enumerator = self._image.Measurements.GetEnumerator()
                idx = 0
                while enumerator.MoveNext():
                    current = enumerator.Current
                    if current == measurement:
                        index = idx
                        break
                    idx += 1

            if not measurement_exists or index is None:
                index = self._image.Measurements.Count

            index = 0 if index is None else index
            return index

        except Exception as e:
            self.logger.error(f"Error getting measurement index: {str(e)}")
            return None

    def _update_measurements_indexes(self) -> None:
        """
        Update measurement indexes in both SDK collection and internal dictionary
        to maintain synchronization.
        """
        try:
            with self._service_lock:
                # Get current measurements from SDK
                sdk_measurements = list(self._image.Measurements)

                # Create new measurements list with correct ordering
                updated_measurements = []

                # Update indexes for each measurement in SDK collection
                for sdk_index, sdk_measurement in enumerate(sdk_measurements):
                    # Find corresponding measurement in internal collection
                    for measurement_dict in self._measurements["measurements"]:
                        if measurement_dict["measurement"] == sdk_measurement:
                            # Update index in measurement dictionary
                            measurement_dict["index"] = sdk_index
                            updated_measurements.append(measurement_dict)
                            self.logger.debug(
                                f"Updated measurement index: {measurement_dict.get('name')} -> {sdk_index}"
                            )
                            break

                # Replace internal measurements list with updated one
                self._measurements["measurements"] = updated_measurements

                # Validate synchronization
                if len(updated_measurements) != len(sdk_measurements):
                    self.logger.warning(
                        "Measurement count mismatch between SDK and internal collection"
                    )

        except Exception as e:
            self.logger.error(f"Error updating measurement indexes: {str(e)}")
            raise

    def _build_measurements_dict(
        self,
        measurement: Any = None,
        measurement_index: Optional[int] = None,
        measurement_config: Optional[Dict[str, Any]] = None,
        measurement_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Helper function to build a standardized measurement dictionary.

        Args:
            measurement: The measurement object
            measurement_index: Index of the measurement in collection
            measurement_config: Configuration dictionary containing optional parameters
            measurement_type: Type of the measurement

        Returns:
            Dict[str, Any]: Standardized measurement dictionary

        Raises:
            ValueError: If measurement object not provided or invalid parameters
        """
        try:
            if not measurement:
                raise ValueError("Measurement object not provided")

            # Initialize default values
            measurement_config = measurement_config or {}

            # Get measurement index and existence
            if measurement_index is None:
                measurement_index = self._get_measurements_index(measurement)

            measurement_exists = self._check_measurements_exists(measurement)

            # Determine type if not provided
            if measurement_type is None and hasattr(measurement, "GetType"):
                measurement_type = measurement.GetType().Name

            # Ensure measurement_type is not None before proceeding
            if measurement_type is None:
                measurement_type = "unknown"

            # Get temperature values if available
            temperature_values = None
            if hasattr(measurement, "GetValues"):
                if measurement_type in ("spot", "delta"):
                    temperature_values = measurement.Value.Value
                elif measurement_type in (
                    "rectangle",
                    "ellipse",
                    "line",
                    "polygon",
                    "polyline",
                ):
                    temperature_values = measurement.Average.Value

            parameters_dict = {}
            if hasattr(measurement, "ThermalParameters"):
                parameters_dict = self._build_thermal_parameters_dict(
                    measurement.ThermalParameters
                )

            values = self.extract_measurement_values(
                measurement=measurement, measurement_type=measurement_type
            )

            id = (
                measurement.Identity.ToString()
                if hasattr(measurement, "Identity")
                else None
            )

            # Build the dictionary
            measurement_dict = {
                "measurement": measurement,
                "id": id,
                "index": measurement_index,
                "Identity": (
                    measurement.Identity if hasattr(measurement, "Identity") else None
                ),
                "name": measurement_config.get("name")
                or getattr(measurement, "Name", None),
                "type": measurement_type,
                "active": measurement_config.get("active", True),
                "temperature": temperature_values,
                "parameters": parameters_dict,
                "shape": measurement_config.get("shape"),
                "config": measurement_config,
                "color": measurement_config.get("color", "#000000"),
                "values": values,
            }

            self.logger.debug(f"Built measurement dictionary: {measurement_dict}")
            return measurement_dict

        except Exception as e:
            self.logger.error(f"Error building measurement dictionary: {str(e)}")
            raise

    def _build_thermal_parameters_dict(self, parameters: Any) -> Dict[str, Any]:
        """
        Convert MeasurementParameters to a dictionary containing all thermal parameters.

        Args:
            parameters: MeasurementParameters object from FLIR SDK

        Returns:
            Dict[str, Any]: Dictionary containing thermal parameters:
                - distance: Distance between object and camera lens (meters)
                - emissivity: Object emissivity value (0-1)
                - reflected_temperature: Reflected apparent temperature
                - use_custom_parameters: Whether using custom parameters
        """
        try:
            if not parameters:
                return {}

            return {
                "distance": object_handler.serialize_with_type_conversion(
                    parameters.Distance, target_type="float", precision=2
                ),
                "emissivity": object_handler.serialize_with_type_conversion(
                    parameters.Emissivity, target_type="float", precision=2
                ),
                "reflected_temperature": object_handler.serialize_with_type_conversion(
                    parameters.ReflectedTemperature, target_type="float", precision=2
                ),
                "use_custom_parameters": object_handler.serialize_with_type_conversion(
                    parameters.UseCustomObjectParameters, target_type="bool"
                ),
            }
        except Exception as e:
            self.logger.error(f"Error building thermal parameters dictionary: {e}")
            return {}

    def extract_measurement_values(
        self, measurement: Any, measurement_type: str
    ) -> Dict[str, Any]:
        """
        Extract all relevant values from a measurement object based on its type.
        Normalizes the output format across different measurement types.

        Args:
            measurement: The measurement object from FLIR SDK
            measurement_type: Type of measurement ('rectangle', 'spot', 'line', 'ellipse', 'polygon')

        Returns:
            Dict containing normalized measurement values:
                - location: Position information (x,y, width, height, points etc)
                - temperature: Temperature readings (min, max, avg, value)
                - area: Area calculations if applicable
                - length: Length calculations if applicable
                - settings: Measurement display settings
        """
        try:
            result: Dict[str, Any] = {
                "location": {},
                "temperature": {},
                "area": {},
                "length": {},
                "settings": {},
            }

            # Common temperature properties for area measurements
            if measurement_type in ["rectangle", "ellipse", "line", "polygon"]:
                if hasattr(measurement, "Min"):
                    result["temperature"]["min"] = measurement.Min.Value
                if hasattr(measurement, "Max"):
                    result["temperature"]["max"] = measurement.Max.Value
                if hasattr(measurement, "Average"):
                    result["temperature"]["average"] = measurement.Average.Value
                if hasattr(measurement, "HotSpot"):
                    result["temperature"]["hot_spot"] = {
                        "x": measurement.HotSpot.X,
                        "y": measurement.HotSpot.Y,
                        "value": measurement.Max.Value,
                    }
                if hasattr(measurement, "ColdSpot"):
                    result["temperature"]["cold_spot"] = {
                        "x": measurement.ColdSpot.X,
                        "y": measurement.ColdSpot.Y,
                        "value": measurement.Min.Value,
                    }

            # Specific properties by type
            if measurement_type == "spot":
                if hasattr(measurement, "Value"):
                    result["temperature"]["value"] = measurement.Value.Value
                if hasattr(measurement, "Point"):
                    result["location"] = {
                        "x": measurement.Point.X,
                        "y": measurement.Point.Y,
                    }

            elif measurement_type in ["rectangle", "ellipse"]:
                if hasattr(measurement, "Location"):
                    result["location"] = {
                        "x": measurement.Location.X,
                        "y": measurement.Location.Y,
                        "width": measurement.Width,
                        "height": measurement.Height,
                    }
                if hasattr(measurement, "ObjectArea"):
                    result["area"]["value"] = measurement.ObjectArea.Value

            elif measurement_type == "line":
                if hasattr(measurement, "Start") and hasattr(measurement, "End"):
                    result["location"] = {
                        "start": {"x": measurement.Start.X, "y": measurement.Start.Y},
                        "end": {"x": measurement.End.X, "y": measurement.End.Y},
                    }
                if hasattr(measurement, "ObjectLength"):
                    result["length"]["value"] = measurement.ObjectLength.Value

            elif measurement_type == "polygon":
                if hasattr(measurement, "Points"):
                    result["location"]["points"] = [
                        {"x": point.X, "y": point.Y} for point in measurement.Points
                    ]
                if hasattr(measurement, "ObjectArea"):
                    result["area"]["value"] = measurement.ObjectArea.Value

            # Common display settings
            common_settings = {
                "IsHotSpotEnabled": "hot_spot_enabled",
                "IsHotSpotMarkerVisible": "hot_spot_marker_visible",
                "IsColdSpotEnabled": "cold_spot_enabled",
                "IsColdSpotMarkerVisible": "cold_spot_marker_visible",
                "IsAverageEnabled": "average_enabled",
                "IsAreaEnabled": "area_enabled",
                "IsLengthEnabled": "length_enabled",
            }

            for sdk_name, result_name in common_settings.items():
                if hasattr(measurement, sdk_name):
                    result["settings"][result_name] = getattr(measurement, sdk_name)

            # Raw values array if available
            if hasattr(measurement, "GetValues"):
                values = measurement.GetValues()
                if values and len(values) > 0:
                    result["temperature"]["raw_values"] = list(values)

            return result

        except Exception as e:
            self.logger.error(f"Error extracting measurement values: {e}")
            return {}

    def update_settings(self):
        """
        Initialize all settings by calling the respective get methods.
        """
        pass
        # TODO: Implementar
        # self.distance = self.get_distance()
        # self.emissivity = self.get_emissivity()
        # self.reflected_temperature = self.get_reflected_temperature()
        # self.use_custom_object_parameters = self.get_use_custom_object_parameters()
        # self.scan_line_start = self.get_scan_line_start()
        # self.scan_line_items = self.get_scan_line_items()
        # self.scan_line_float_start = self.get_scan_line_float_start()
        # self.scan_line_float_items = self.get_scan_line_float_items()

    def to_string(self) -> dict:
        """
        Return all properties in JSON format.

        Returns:
            dict: JSON string of all properties.
        """
        # json_dict = {
        #     # "measurement_event_args_handler": self.measurement_event_args_handler.to_string(),
        #     # "measurement_shape_handler": self.measurement_shape_handler.to_string(),
        #     "distance": self.distance,
        #     "emissivity": self.emissivity,
        #     "reflected_temperature": self.reflected_temperature,
        #     "use_custom_object_parameters": self.use_custom_object_parameters,
        #     "scan_line_start": self.scan_line_start,
        #     "scan_line_items": self.scan_line_items,
        #     "scan_line_float_start": self.scan_line_float_start,
        #     "scan_line_float_items": self.scan_line_float_items,
        # }

        json_dict = {}

        measurements_data = {
            "measurements": [
                {
                    "id": m["id"],
                    "name": m["name"],
                    "type": m["type"],
                    "active": m["active"],
                    # "bounds": m["bounds"],
                }
                for m in self._measurements["measurements"]
            ]
        }
        json_dict.update(measurements_data)

        return json_dict

    def to_dict(self) -> dict:
        try:
            measurements_dict = self.get_all_measurements(rasterize=True)
        except Exception as e:
            self.logger.error(f"Error retrieving measurements: {e}")

        ms_dict = self.to_dict()

        #
        return measurements_dict

    """
    TODO: 

    2. Sincronização de Propriedades
    Problema:
    As propriedades como distance armazenam valores em variáveis de instância (self._distance), mas os getters/setters acessam diretamente o SDK. Isso pode levar a dados desatualizados.

    Solução:
    Remova as variáveis de instância redundantes e acesse o SDK diretamente nas propriedades:

    @property
    def distance(self) -> Optional[float]:
        try:
            return self.thermal_image_file.RadiometricSettings.Distance
        except Exception as e:
            self.logger.error(f"Erro ao obter distância: {e}")
            return None
    
    3. Validação de Tipos e Inputs
    Problema:
    Métodos como set_scan_line_start aceitam Image.Point, mas não há validação se o objeto é válido.

    Solução:
    Adicione validações para garantir integridade:

    def set_scan_line_start(self, value: Image.Point):
        if not isinstance(value, Image.Point):
            raise TypeError("O valor deve ser um Image.Point.")
        # ... restante do código
    4. Thread Safety
    Problema:
    Não há garantia de thread safety se a câmera estiver capturando imagens em tempo real.

    Solução:
    Adicione locks em operações críticas:

    from threading import Lock

    class CameraMeasurements:
        def __init__(self, _camera):
            self._lock = Lock()
        
        def set_distance(self, value: float):
            with self._lock:
                try:
                    self.thermal_image_file.RadiometricSettings.Distance = value
                except Exception as e:
                    # ... tratamento

        
    """
