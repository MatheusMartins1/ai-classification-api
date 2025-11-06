"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

import datetime
import os
from enum import Enum
from typing import Any, Dict, Iterator, List, Literal, Optional

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

import Flir.Atlas.Image as Image  # type: ignore

# Import the necessary classes from the assembly
import Flir.Atlas.Live as live  # type: ignore

# WebSocket/Message Broker
from camera._delete.events import EventBus as ws
from camera.image.alarms.humidity_alarm import HumidityAlarmManager
from camera.image.alarms.insulation_alarm import InsulationAlarmManager
from camera.image.alarms.iso_therms import IsothermsManager


class IsothermType(str, Enum):
    """Enum for isotherm types"""

    ABOVE = "above"
    BELOW = "below"
    INTERVAL = "interval"


class Alarm:
    """
    A class to represent the Alarm from Flir's Atlas SDK.
    """

    def __init__(self, _camera):
        """
        Initialize the Alarm class with a FlirAlarm instance.

        """
        self._camera = _camera
        self.logger = _camera.logger

        self._image = _camera.image_obj_thermal

        # self._alarms_enum = Image.Alarms.GetEnumerator()
        self._alarms = {"alarms": [], "iso_therms": []}
        self._alarms_trigger = {"alarms": [], "iso_therms": []}

        self.initialize()

    def initialize(self) -> None:
        """
        Initialize the Alarm class.
        """
        if not self._camera.is_thermal_image_supported:
            return

        try:
            alarms_enum = self._image.Alarms.GetEnumerator()
        except Exception as e:
            self.logger.error(e)

        try:
            iso_enum = self._image.Isotherms.GetEnumerator()
        except Exception as e:
            self.logger.error(iso_enum)

        if not alarms_enum and not iso_enum:
            return

        # Process standard alarms
        if alarms_enum is not None:
            # Convert to list to avoid enumeration issues
            alarms_list = list(self._image.Alarms)

            alarms_count = self._image.Alarms.Count

            # TODO: check interator
            for id, current_alarm in enumerate(alarms_list):
                if current_alarm is not None:
                    alarm_dict = self._build_alarm_dict(
                        alarm=current_alarm, alarm_index=id
                    )
                    self._alarms["alarms"].append(alarm_dict)

        # Process isotherms
        if iso_enum is not None:
            # Convert to list to avoid enumeration issues
            iso_list = list(self._image.Isotherms)

            iso_count = self._image.Isotherms.Count

            # TODO: check interator
            for id, current_alarm in enumerate(iso_list):
                if current_alarm is not None:
                    alarm_dict = self._build_alarm_dict(
                        alarm=current_alarm, alarm_index=id
                    )
                    self._alarms["iso_therms"].append(alarm_dict)

    def clear_all(self) -> None:
        """
        Clears all alarms and isotherms from their respective collections.
        """
        try:
            # TEST: if this is the correct way to clear alarms
            # Probably is self._image.Alarms.ClearAll()
            # Clear standard alarms
            Image.Alarms.ClearAll()
            self._alarms["alarms"].clear()

            # Clear isotherms
            Image.Isotherms.IsothermCollection.ClearAll()
            self._alarms["iso_therms"].clear()

            self._alarms = {"alarms": [], "iso_therms": []}

            self.logger.info("All alarms and isotherms cleared successfully")

            ws.publish(event="alarm_cleared", data=self._alarms)
        except Exception as e:
            self.logger.error(f"Error clearing alarms: {str(e)}")
            raise

    # TODO: Implement
    def on_alarm_event_change(self, sender, e) -> None:
        """
        Handle events when an alarm property changes.

        Args:
            sender: The object that triggered the event
            e: AlarmEventArgs containing alarm change information
        """
        try:
            self.logger.info("Alarm event triggered")

            self._update_alarm_indexes(collection_type="alarms")

            # Get the alarm that changed
            alarm = e.Alarm

            alarm_dict = self._build_alarm_dict(
                alarm=alarm, alarm_event=e, collection_type="alarms"
            )

            # Log detailed alarm information
            self.logger.info(alarm_dict)

            # TODO: Implement
            # if alarm.GetType().Name == "HumidityAlarm":
            #     alarm_obj = HumidityAlarmManager(alarm)
            # elif alarm.GetType().Name == "InsulationAlarm":
            #     alarm_obj = InsulationAlarmManager(alarm)

            # alarm_dict["alarm_obj"] = alarm_obj

            ws.publish(event="alarm_changed", data=self._alarms)

            try:
                alarm_index = alarm_dict.get("alarm_index")
                if alarm_index is not None and 0 <= alarm_index < len(
                    self._alarms["alarms"]
                ):
                    self._alarms["alarms"][alarm_index].update(alarm_dict)
                else:
                    self._alarms["alarms"].append(alarm_dict)
            except Exception as ex:
                self.logger.error(f"Error updating alarms list: {str(ex)}")

        except Exception as ex:
            self.logger.error(f"Error handling alarm event: {str(ex)}")

    # TODO: Implement
    def on_alarm_iso_event_change(self, sender, e) -> None:
        """
        Handle events when an alarm property changes.

        Args:
            sender: The object that triggered the event
            e: AlarmEventArgs containing alarm change information
        """
        try:
            alarm = e.Isotherm
            temp = alarm.Threshold
            temp_unit = self._image.TemperatureUnit
            unit_from = temp_unit.ToString()
            unit_to = "Celsius"
            temp = self._camera.convert_temperature_unit(
                temperature=temp,
                unit_from=unit_from,
                unit_to=unit_to,
            )
            # enabled = alarm.Enabled
            color = alarm.Color

            # Verifica o tipo do alarme
            if isinstance(alarm, Image.Isotherms.AlarmIsothermAbove):
                # Alarme de temperatura acima do limite
                self.logger.info(f"Alarme: Temperatura acima de {temp}°C")

            elif isinstance(alarm, Image.Isotherms.AlarmIsothermBelow):
                # Alarme de temperatura abaixo do limite
                self.logger.info(f"Alarme: Temperatura abaixo de {temp}°C")

            elif isinstance(alarm, Image.Isotherms.AlarmIsothermInterval):
                # Alarme de temperatura abaixo do limite
                self.logger.info(f"Alarme: Temperatura de intervalo de {temp}°C")
            else:
                return

            # Publica o evento via websocket
            ws.publish(
                "alarm_triggered",
                {
                    "type": str(type(alarm)),
                    "temperature": temp,
                    "timestamp": datetime.datetime.now().isoformat(),
                },
            )

        except Exception as ex:
            self.logger.error(f"Error handling isotherm event: {str(ex)}")

    def update_alarm(
        self,
        alarm: Any,
        alarm_type: Literal["humidity", "insulation", "above", "below", "interval"],
        config: Dict[str, Any] = None,
        collection_type: Literal["alarms", "iso_therms"] = None,
    ) -> None:
        """
        Update an existing alarm with new configuration.

        Args:
            alarm: The alarm object to update
            alarm_type: Type of alarm to update
            config: Dictionary containing alarm configuration parameters
            collection_type: Type of collection the alarm belongs to

        Raises:
            ValueError: If alarm doesn't exist or invalid parameters provided
        """
        if not config:
            config = {}

        if not collection_type:
            collection_type = (
                "iso_therms"
                if alarm_type in IsothermType.__members__.values()
                else "alarms"
            )

        try:
            # Verify alarm exists
            if not self._check_alarm_exists(alarm, collection_type):
                raise ValueError(f"Alarm not found in {collection_type} collection")

            # Update the alarm based on type
            if collection_type == "alarms":
                updated_alarm = self._handle_standard_alarm(alarm_type, config)
            elif collection_type == "iso_therms":
                updated_alarm = self._handle_isotherm_alarm(alarm_type, config)
            else:
                raise ValueError(f"Invalid collection type: {collection_type}")

            if updated_alarm:
                self.logger.info(f"Updated alarm: {updated_alarm}")

        except Exception as ex:
            self.logger.error(f"Error updating alarm: {ex}")
            raise

    def add_alarm(
        self,
        alarm_type: Literal["humidity", "insulation", "above", "below", "interval"],
        config: Dict[str, Any] = None,
        collection_type: Literal["alarms", "iso_therms"] = None,
    ) -> None:
        """
        Add an alarm to the camera with specified configuration.

        Args:
            alarm_type: Type of alarm to add
            config: Dictionary containing alarm configuration parameters
            collection_type: Type of collection to add alarm to

        Raises:
            ValueError: If invalid alarm_type or collection_type is provided
        """
        self.logger.info(f"Add alarm - {config.get('name')}")
        if not config:
            config = {}

        if not collection_type:
            collection_type = (
                "iso_therms"
                if alarm_type in IsothermType.__members__.values()
                else "alarms"
            )

        try:
            alarm = None

            if collection_type == "alarms":
                alarm = self._handle_standard_alarm(alarm_type, config)
            elif collection_type == "iso_therms":
                alarm = self._handle_isotherm_alarm(alarm_type, config)
            else:
                raise ValueError(f"Invalid collection type: {collection_type}")

        except Exception as ex:
            self.logger.error(f"Error adding alarm: {ex}")
            raise

        if alarm:
            alarm_dict = self._build_alarm_dict(
                alarm=alarm,
                config=config,
                alarm_type=alarm_type,
                collection_type=collection_type,
            )

            alarm_dict["alarm"] = alarm
            self._alarms[collection_type].append(alarm)

            # self._update_alarm_indexes(collection_type=collection_type)

            self.logger.info(f"Added alarm to list: {alarm}")
            ws.publish(event="alarm_added", data=self._alarms)

    def on_alarm_added_event(self, sender, e) -> None:
        """
        Handle alarm added events from both standard alarms and isotherms.

        Args:
            sender: The object that triggered the event
            e: AlarmEventArgsManager containing alarm/isotherm event information

        Note:
            This method updates the internal alarm collections based on the event type
        """
        try:
            # Infer collection type from event
            collection_type = self._infer_collection_type(event=e)

            # Get the appropriate alarm object based on collection type
            alarm = e.Alarm if collection_type == "alarms" else e.Isotherm

            if not alarm:
                raise ValueError("No alarm object found in event")

            # Build standardized alarm dictionary
            alarm_dict = self._build_alarm_dict(
                alarm=alarm, alarm_event=e, collection_type=collection_type
            )

            # Log the alarm information
            self.logger.info(f"New {collection_type} alarm added: {alarm_dict}")

            # Get the alarm index
            alarm_index = alarm_dict.get("alarm_index")

            # Update or append based on index validity
            if alarm_index is not None and 0 <= alarm_index < len(
                self._alarms[collection_type]
            ):
                # Update existing alarm
                self._alarms[collection_type][alarm_index].update(alarm_dict)
                self.logger.debug(
                    f"Updated existing {collection_type} at index {alarm_index}"
                )
            else:
                # Append new alarm
                self._alarms[collection_type].append(alarm_dict)
                self._update_alarm_indexes(collection_type)  # Add this line
                self.logger.debug(f"Added new {collection_type} alarm")

            ws.publish(event="alarm_added", data=self._alarms)
        except Exception as ex:
            self.logger.error(f"Error in alarm added event handler: {str(ex)}")
            raise

    def remove_alarm(
        self, alarm_index: int, collection_type: Literal["alarms", "iso_therms"]
    ) -> None:
        """
        Remove an alarm from SDK collection by index.

        Args:
            alarm_index: Index of the alarm to remove
            collection_type: Type of collection the alarm belongs to

        Raises:
            ValueError: If index is invalid or collection type is incorrect
        """
        try:
            # Validate index
            if not 0 <= alarm_index < len(self._alarms[collection_type]):
                raise ValueError(f"Invalid alarm index: {alarm_index}")

            # Get the alarm to remove from internal tracking
            alarm_to_remove = self._alarms[collection_type][alarm_index].get("alarm")
            if not alarm_to_remove:
                raise ValueError(f"No alarm found at index {alarm_index}")

            # Remove from SDK collection only - event handler will update internal list
            if collection_type == "alarms":
                self._image.Alarms.Remove(alarm_to_remove)
            else:
                self._image.Isotherms.Remove(alarm_to_remove)

            self.logger.info(f"Removed alarm from SDK {collection_type} collection")

        except Exception as ex:
            self.logger.error(f"Error removing alarm at index {alarm_index}: {ex}")
            raise

    def on_alarm_removed_event(self, sender, e) -> None:
        """
        Handle alarm removed events from both standard alarms and isotherms.

        Args:
            sender: The object that triggered the event
            e: AlarmEventArgsManager containing alarm/isotherm event information

        Note:
            This method updates the internal alarm collections by removing the specified alarm
        """
        try:
            # Infer collection type from event
            collection_type = self._infer_collection_type(event=e)

            # Get the appropriate alarm object based on collection type
            alarm = e.Alarm if collection_type == "alarms" else e.Isotherm

            if not alarm:
                raise ValueError("No alarm object found in event")

            # Get the alarm index from the collection
            alarm_exists = self._check_alarm_exists(alarm, collection_type)
            if alarm_exists:
                for idx, stored_alarm in enumerate(self._alarms[collection_type]):
                    if stored_alarm["alarm"] == alarm:
                        # Remove the alarm from our internal collection
                        removed_alarm = self._alarms[collection_type].pop(idx)
                        self._update_alarm_indexes(collection_type)  # Add this line
                        self.logger.info(
                            f"Removed {collection_type} alarm at index {idx}: {removed_alarm}"
                        )
                        break
            else:
                self.logger.warning(
                    f"Attempted to remove non-existent {collection_type} alarm"
                )

            ws.publish(event="alarm_removed", data=self._alarms)
        except Exception as ex:
            self.logger.error(f"Error in alarm removed event handler: {str(ex)}")
            raise

    def add_humidity_alarm(
        self,
        name: str,
        atmospheric_temperature: float,
        relative_air_humidity: float,
        relative_humidity_alarm_level: float,
    ) -> HumidityAlarmManager:
        """
        Creates and adds a humidity alarms.

        :param name: The specified name.
        :param atmospheric_temperature: The specified atmospheric temperature.
        :param relative_air_humidity: The specified relative air humidity.
        :param relative_humidity_alarm_level: The specified relative humidity alarms level.
        :return: The HumidityAlarmManager.
        """
        return Image.Alarms.AddHumidityAlarms(
            name,
            atmospheric_temperature,
            relative_air_humidity,
            relative_humidity_alarm_level,
        )

    def add_insulation_alarm(
        self,
        name: str,
        indoor_air_temperature: float,
        outdoor_air_temperature: float,
        insulation_factor: float,
    ) -> InsulationAlarmManager:
        """
        Creates and adds an insulation alarms.

        :param name: The specified name.
        :param indoor_air_temperature: The specified indoor air temperature.
        :param outdoor_air_temperature: The specified outdoor air temperature.
        :param insulation_factor: The specified insulation factor.
        :return: The InsulationAlarmManager.
        """
        return Image.Alarms.AddInsulationAlarm(
            name, indoor_air_temperature, outdoor_air_temperature, insulation_factor
        )

    def _check_alarm_exists(self, alarm, collection_type: str) -> bool:
        """
        Check if alarm exists in the specified collection.

        Args:
            alarm: The alarm object to check
            collection_type: Either "alarms" or "iso_therms"

        Returns:
            bool: True if alarm exists, False otherwise
        """
        try:
            if collection_type == "alarms":
                return self._image.Alarms.Contains(alarm)
            elif collection_type == "iso_therms":
                return self._image.Isotherms.Contains(alarm)
            return False
        except Exception as e:
            self.logger.error(f"Error checking if alarm exists: {str(e)}")
            return False

    def _infer_collection_type(
        self, alarm: Any = None, event: Any = None
    ) -> Literal["alarms", "iso_therms"]:
        """
        Infer the collection type based on alarm object and event properties.

        Args:
            alarm: The alarm object to check
            event: The event object that triggered the alarm (optional)

        Returns:
            Literal["alarms", "iso_therms"]: The inferred collection type

        Raises:
            ValueError: If neither alarm nor event can be used to infer type
        """
        if not alarm and not event:
            raise ValueError("Neither alarm nor event object provided")

        # Try to infer from alarm object first
        if alarm:
            if hasattr(alarm, "IsothermType"):
                return "iso_therms"
            elif hasattr(alarm, "GetType"):
                return "alarms"

        # If can't infer from alarm, try from event
        if event:
            if hasattr(event, "Isotherm"):
                return "iso_therms"
            elif hasattr(event, "Alarm"):
                return "alarms"

        raise ValueError("Could not infer type from either alarm or event object")

    def _get_alarm_index(self, alarm: Any, collection_type: str) -> Optional[int]:
        """
        Get the index of an alarm in its respective collection. If alarm doesn't exist,
        return the next available index based on collection count.

        Args:
            alarm: The alarm object to find the index for
            collection_type: The type of collection ("alarms" or "iso_therms")

        Returns:
            Optional[int]: The index of the alarm if found or next available index, None if error
        """
        try:
            alarm_exists = self._check_alarm_exists(alarm, collection_type)
            index = None

            if collection_type == "alarms":
                if alarm_exists:
                    enumerator = self._image.Alarms.GetEnumerator()
                    idx = 0
                    while enumerator.MoveNext():
                        current = enumerator.Current
                        if current == alarm:
                            index = idx
                            break
                        idx += 1

                if not alarm_exists or index is None:
                    index = self._image.Alarms.Count

            elif collection_type == "iso_therms":
                if alarm_exists:
                    enumerator = self._image.Isotherms.GetEnumerator()
                    idx = 0
                    while enumerator.MoveNext():
                        current = enumerator.Current
                        if current == alarm:
                            index = idx
                            break
                        idx += 1

                if not alarm_exists or index is None:
                    index = self._image.Isotherms.Count

            index = 0 if index is None else index
            return index

        except Exception as e:
            self.logger.error(f"Error getting alarm index: {str(e)}")
            return None

    def _handle_standard_alarm(self, alarm_type: str, config: dict) -> Optional[Any]:
        """Handle creation of standard alarms"""
        temp_unit = self._image.TemperatureUnit
        unit_from = temp_unit.ToString()
        unit_to = "Celsius"  # TODO: get from env/variable
        if alarm_type == "humidity":

            atmospheric_temp = (
                self._camera.convert_temperature_unit(
                    temperature=config.get("atmospheric_temperature", 20),
                    unit_from=unit_from,
                    unit_to=unit_to,
                )
                if temp_unit != "Celsius"
                else config.get("atmospheric_temperature", 20)
            )
            return self._image.Alarms.AddHumidityAlarms(
                config.get("name", "Humidity Alarm"),
                atmospheric_temp,
                config.get("relative_humidity", 0.40),
                config.get("humidity_alarm_level", 0.70),
            )

        elif alarm_type == "insulation":
            indoor_temp = self._camera.convert_temperature_unit(
                temperature=config.get("indoor_temperature", 20),
                unit_from=unit_from,
                unit_to=unit_to,
            )
            outdoor_temp = self._camera.convert_temperature_unit(
                temperature=config.get("outdoor_temperature", 10),
                unit_from=unit_from,
                unit_to=unit_to,
            )
            return self._image.Alarms.AddInsulationAlarm(
                config.get("name", "Insulation Alarm"),
                indoor_temp,
                outdoor_temp,
                config.get("insulation_factor", 0.7),
            )

        return None

    def _handle_isotherm_alarm(self, alarm_type: str, config: dict) -> Optional[Any]:
        """
        Handle creation and configuration of isotherm alarms

        Args:
            alarm_type: Type of isotherm alarm
            config: Dictionary containing configuration parameters
        """
        try:
            iso = None
            threshold_temp = None
            temp_unit = self._image.TemperatureUnit
            unit_from = temp_unit.ToString()
            unit_to = "Celsius"

            if unit_to != unit_from:
                threshold_temp = self._camera.convert_temperature_unit(
                    temperature=config.get("threshold", 30.0),
                    unit_from=unit_from,
                    unit_to=unit_to,
                )
            else:
                threshold_temp = config.get("threshold", 30.0)

            if alarm_type == "above":
                iso = self._image.Isotherms.AddAbove()
                if iso:
                    iso.Threshold = threshold_temp

            elif alarm_type == "below":
                iso = self._image.Isotherms.AddBelow()
                if iso:
                    iso.Threshold = threshold_temp

            elif alarm_type == "interval":
                iso = self._image.Isotherms.AddInterval()
                if iso:
                    # Convert min/max temperatures from Celsius to Kelvin
                    min_temp = self._camera.convert_temperature_unit(
                        temperature=config.get("minimum", 20.0),
                        unit_from=unit_from,
                        unit_to=unit_to,
                    )
                    max_temp = self._camera.convert_temperature_unit(
                        temperature=config.get("maximum", 30.0),
                        unit_from=unit_from,
                        unit_to=unit_to,
                    )
                    iso.Interval = (min_temp, max_temp)
                    self.logger.info(f"iso : {iso}")

            if iso:

                # self._configure_isotherm(iso, config)

                self.logger.info(f"Added isotherm alarm: {iso}")

                # Add name if provided
                if config.get("name") and hasattr(iso, "Name"):
                    iso.Name = config.get("name")

            return iso

        except Exception as e:
            self.logger.error(f"Error creating isotherm alarm: {str(e)}")
            raise

    def _configure_isotherm(self, iso: Any, config: dict) -> None:
        """
        Configure common isotherm properties according to Flir.Atlas.Image.Isotherms.Isotherm specification

        Args:
            iso: Isotherm object to configure
            config: Configuration dictionary containing:
                - color: Main color of the isotherm
                - contrast_color: Contrast color for the isotherm (optional)
                - appearance: Appearance settings for the isotherm (optional)
        """
        # TODO: separate and use System.Drawing.Color...
        try:
            if hasattr(iso, "Color"):
                iso.Color = config.get("color", iso.Color)
        except Exception as e:
            self.logger.error(f"Error configuring isotherm: {str(e)}")
            # TODO: separate and use System.Drawing.Color...
        try:
            if hasattr(iso, "ContrastColor") and "contrast_color" in config:
                iso.ContrastColor = config.get("contrast_color")
        except Exception as e:
            self.logger.error(f"Error configuring isotherm: {str(e)}")

        # TODO: separate and use System.Drawing.Color...
        try:
            if hasattr(iso, "Appearance") and "appearance" in config:
                iso.Appearance = config.get("appearance")
        except Exception as e:
            self.logger.error(f"Error configuring isotherm: {str(e)}")

    def _update_alarm_indexes(
        self, collection_type: Literal["alarms", "iso_therms"]
    ) -> None:
        """
        Update alarm indexes in both SDK collection and internal dictionary
        to maintain synchronization.

        Args:
            collection_type: Type of collection to update indexes for
        """
        try:
            with self._camera._camera_lock:
                # Get current alarms from SDK based on collection type
                sdk_alarms = list(
                    self._image.Alarms
                    if collection_type == "alarms"
                    else self._image.Isotherms
                )

                # Create new alarms list with correct ordering
                updated_alarms = []

                # Update indexes for each alarm in SDK collection
                for sdk_index, sdk_alarm in enumerate(sdk_alarms):
                    # Find corresponding alarm in internal collection
                    for alarm_dict in self._alarms[collection_type]:
                        if alarm_dict["alarm"] == sdk_alarm:
                            # Update index in alarm dictionary
                            alarm_dict["alarm_index"] = sdk_index
                            updated_alarms.append(alarm_dict)
                            self.logger.debug(
                                f"Updated {collection_type} alarm index: "
                                f"{alarm_dict.get('name')} -> {sdk_index}"
                            )
                            break

                # Replace internal alarms list with updated one
                self._alarms[collection_type] = updated_alarms

                # Validate synchronization
                if len(updated_alarms) != len(sdk_alarms):
                    self.logger.warning(
                        f"{collection_type} count mismatch between SDK "
                        f"({len(sdk_alarms)}) and internal collection "
                        f"({len(updated_alarms)})"
                    )

        except Exception as e:
            self.logger.error(f"Error updating {collection_type} indexes: {str(e)}")
            raise

    def _build_alarm_dict(
        self,
        alarm: Any = None,
        alarm_index: Optional[int] = None,
        alarm_event: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        alarm_type: Optional[
            Literal["humidity", "insulation", "above", "below", "interval"]
        ] = None,
        collection_type: Optional[Literal["alarms", "iso_therms"]] = None,
    ) -> Dict[str, Any]:
        """
        Helper function to build a standardized alarm dictionary with inferred values.

        Args:
            alarm: The alarm object
            alarm_index: Index of the alarm in collection
            alarm_event: Event object if triggered by event
            config: Configuration dictionary containing optional user and name
            alarm_type: Type of the alarm (optional, will be inferred if not provided)
            collection_type: Type of collection (optional, will be inferred if not provided)

        Returns:
            Dict[str, Any]: Standardized alarm dictionary

        Raises:
            ValueError: If alarm type cannot be inferred or invalid parameters
        """
        # Initialize default values
        config = config or {}
        type_value = None

        # Infer collection type if not provided
        if alarm:
            if hasattr(alarm, "IsothermType"):
                collection_type = "iso_therms"
            elif hasattr(alarm, "GetType"):
                collection_type = "alarms"
            else:
                raise ValueError("Could not infer Alarm type")
        else:
            raise ValueError("Alarm object not provided")

        # Get type value based on collection type
        if collection_type == "iso_therms" and hasattr(alarm, "IsothermType"):
            type_value = alarm.IsothermType
        elif collection_type == "alarms" and hasattr(alarm, "GetType"):
            type_value = alarm.GetType().Name

        # Infer alarm type if not provided
        if alarm_type is None and type_value:
            type_mapping = {
                "HumidityAlarm": "humidity",
                "InsulationAlarm": "insulation",
                "Above": "above",
                "Below": "below",
                "Interval": "interval",
            }
            alarm_type = type_mapping.get(type_value, type_value)

        # Update alarm config with name if available
        if hasattr(alarm, "Name") and not config.get("name"):
            config["name"] = alarm.Name

        # Get alarm index and existence
        alarm_index = self._get_alarm_index(alarm, collection_type)

        alarm_exists = self._check_alarm_exists(alarm, collection_type)

        # Determine date created
        try:
            date_created = (
                self._alarms[collection_type][alarm_index]["date_created"]
                if alarm_exists and alarm_index != 0
                else datetime.datetime.now()
            )
        except (KeyError, IndexError, TypeError):
            date_created = datetime.datetime.now()

        # Build and return the dictionary
        return {
            "alarm": alarm,
            "alarm_index": alarm_index,
            "alarm_event": alarm_event,
            "user_created": config.get("user"),
            "name": config.get("name"),
            "type": type_value,
            "alarm_type": alarm_type,
            "config": config,
            "collection_type": collection_type,
            "alarm_obj": None,
            "date_created": date_created,
            "date_updated": datetime.datetime.now(),
        }

    def get_all_alarms(self, rasterize=True) -> Dict:
        """
        Get all alarms.

        Returns:
            List of dictionaries containing measurement information
        """
        if not self._camera.is_thermal_image_supported:
            return {}

        try:
            if rasterize:
                alarms = {}
                alarms["alarms"] = [
                    self._camera.rasterize_alarm(alarm)
                    for alarm in self._alarms["alarms"]
                ]
                alarms["iso_therms"] = [
                    self._camera.rasterize_alarm(alarm)
                    for alarm in self._alarms["iso_therms"]
                ]

                return alarms
            else:
                return self._alarms
        except Exception as e:
            self.logger.error(f"Error getting all alarms: {e}")
            return {}

    def to_string(self) -> dict:
        """
        Return all properties in JSON format.

        Returns:
            dict: JSON string of all properties.
        """
        properties = {
            "isotherm": self.isotherm,
            "iso_indication": self.iso_indication,
            "iso_coverage": self.iso_coverage,
            "name": self.name,
            # "humidity_alarm_handler": {
            #     "atmospheric_temperature": self.humidity_alarm_handler.atmospheric_temperature,
            #     "relative_air_humidity": self.humidity_alarm_handler.relative_air_humidity,
            #     "relative_humidity_alarm_level": self.humidity_alarm_handler.relative_humidity_alarm_level,
            #     "isotherm": self.humidity_alarm_handler.isotherm,
            #     "measurement_rectangle": self.humidity_alarm_handler.measurement_rectangle,
            #     "iso_coverage_threshold": self.humidity_alarm_handler.iso_coverage_threshold,
            # },
            # "insulation_alarm_handler": {
            #     "indoor_air_temperature": self.insulation_alarm_handler.indoor_air_temperature,
            #     "insulation_factor": self.insulation_alarm_handler.insulation_factor,
            #     "outdoor_air_temperature": self.insulation_alarm_handler.outdoor_air_temperature,
            #     "reserved": self.insulation_alarm_handler.reserved,
            #     "isotherm": self.insulation_alarm_handler.isotherm,
            #     "measurement_rectangle": self.insulation_alarm_handler.measurement_rectangle,
            #     "iso_coverage_threshold": self.insulation_alarm_handler.iso_coverage_threshold,
            # },
        }

        return properties
