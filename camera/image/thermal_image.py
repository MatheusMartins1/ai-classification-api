"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

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
from System import DateTime, Guid  # type: ignore


class ThermalImage:
    def __init__(self, _camera):
        self._camera = _camera
        self._image = _camera.image_obj_thermal
        self.logger = _camera.logger

    """ Properties """

    @property
    def jpeg_image(self) -> None | str:
        # TEST:
        """
        Get or set the jpeg representation of the Thermal image.

        Returns:
            Bitmap: The jpeg representation of the Thermal image.
        """
        try:
            return self._image.JpegImage
        except Exception as e:
            self.logger.error(f"Error getting jpeg image: {e}")
            return None

    @jpeg_image.setter
    def jpeg_image(self, value: str) -> None:
        # TEST:
        try:
            self._image.JpegImage = value
        except Exception as e:
            self.logger.error(f"Error setting jpeg image: {e}")

    @property
    def overflow_signal_value(self) -> None | int:
        # TEST:
        """
        Get the overflow signal value.

        Returns:
            int: The overflow signal value.
        """
        try:
            return self._image.OverflowSignalValue
        except Exception as e:
            self.logger.error(f"Error getting overflow signal value: {e}")
            return None

    @property
    def underflow_signal_value(self) -> None | int:
        # TEST:
        """
        Get the underflow signal value.

        Returns:
            int: The underflow signal value.
        """
        try:
            return self._image.UnderflowSignalValue
        except Exception as e:
            self.logger.error(f"Error getting underflow signal value: {e}")
            return None

    @property
    def min_signal_value(self) -> None | int:
        # TEST:
        """
        Get the minimum signal value of the image.

        Returns:
            int: The minimum signal value of the image.
        """
        try:
            return self._image.MinSignalValue
        except Exception as e:
            self.logger.error(f"Error getting minimum signal value: {e}")
            return None

    @property
    def max_signal_value(self) -> None | int:
        # TEST:
        """
        Get the maximum signal value of the image.

        Returns:
            int: The maximum signal value of the image.
        """
        try:
            return self._image.MaxSignalValue
        except Exception as e:
            self.logger.error(f"Error getting maximum signal value: {e}")
            return None

    @property
    def precision(self) -> None | int:
        # TEST:
        """
        Get the presentation precision (number of decimals).

        Returns:
            int: The number of decimals.
        """
        try:
            return self._image.Precision
        except Exception as e:
            self.logger.error(f"Error getting precision: {e}")
            return None

    @property
    def zoom(self) -> None | str:
        # TEST:
        """
        Get the image zoom settings.

        Returns:
            ZoomSettings: The image zoom settings.
        """
        try:
            return self._image.Zoom
        except Exception as e:
            self.logger.error(f"Error getting zoom settings: {e}")
            return None

    @property
    def color_distribution(self) -> None | str:
        # TEST:
        """
        Get or set the Thermal image color distribution.

        Returns:
            ColorDistribution: The Thermal image color distribution.
        """
        try:
            return self._image.ColorDistribution
        except Exception as e:
            self.logger.error(f"Error getting color distribution: {e}")
            return None

    @color_distribution.setter
    def color_distribution(self, value: str) -> None:
        # TEST:
        # value: live.Remote.ColorDistribution
        try:
            self._image.ColorDistribution = value
        except Exception as e:
            self.logger.error(f"Error setting color distribution: {e}")

    @property
    def thermal_measurements(self) -> None | str:
        # TEST:
        """
        Get the advanced measurements calculator.

        Returns:
            Calculator: The advanced measurements calculator.
        """
        try:
            return self._image.ThermalMeasurements
        except Exception as e:
            self.logger.error(f"Error getting thermal measurements: {e}")
            return None

    @property
    def statistics(self) -> None | str:
        # TEST:
        """
        Get the image results ImageStatistics.

        Returns:
            ImageStatistics: The image results ImageStatistics.
        """
        try:
            return self._image.Statistics
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return None

    @property
    def thermal_parameters(self) -> None | str:
        # TEST:
        """
        Get the image object parameters (e.g., emissivity, distance).

        Returns:
            ImageParameters: The image object parameters.
        """
        try:
            return self._image.ThermalParameters
        except Exception as e:
            self.logger.error(f"Error getting thermal parameters: {e}")
            return None

    @property
    def temperature_unit(self) -> None | str:
        # TEST:
        """
        Get or set the temperature unit.

        Returns:
            TemperatureUnit: The temperature unit.
        """
        try:
            return self._image.TemperatureUnit
        except Exception as e:
            self.logger.error(f"Error getting temperature unit: {e}")
            return None

    @temperature_unit.setter
    def temperature_unit(self, value: str) -> None:
        # TEST:
        # live.Remote.TemperatureUnit
        try:
            self._image.TemperatureUnit = value
        except Exception as e:
            self.logger.error(f"Error setting temperature unit: {e}")

    @property
    def distance_unit(self) -> None | str:
        # TEST:
        """
        Get or set the distance unit.

        Returns:
            DistanceUnit: The distance unit.
        """
        try:
            return self._image.DistanceUnit
        except Exception as e:
            self.logger.error(f"Error getting distance unit: {e}")
            return None

    @distance_unit.setter
    def distance_unit(self, value: str) -> None:
        # TEST:
        try:
            self._image.DistanceUnit = value
        except Exception as e:
            self.logger.error(f"Error setting distance unit: {e}")

    @property
    def camera_information(self) -> None | str:
        # TEST:
        """
        Get or set the information about the camera used to create this Thermal image.

        Returns:
            CameraInformation: The camera information.
        """
        try:
            return self._image.CameraInformation
        except Exception as e:
            self.logger.error(f"Error getting camera information: {e}")
            return None

    @camera_information.setter
    def camera_information(self, value: str) -> None:
        # TEST:
        try:
            self._image.CameraInformation = value
        except Exception as e:
            self.logger.error(f"Error setting camera information: {e}")

    @property
    def histogram(self) -> None | str:
        # TEST:
        """
        Get the image histogram.

        Returns:
            Histogram: The image histogram.
        """
        try:
            return self._image.Histogram
        except Exception as e:
            self.logger.error(f"Error getting histogram: {e}")
            return None

    @property
    def measurements(self) -> None | str:
        # TEST:
        """
        Get the measurements collection.

        Returns:
            MeasurementCollection: The measurements collection.
        """
        try:
            return self._image.Measurements
        except Exception as e:
            self.logger.error(f"Error getting measurements: {e}")
            return None

    @property
    def trigger(self) -> None | str:
        # TEST:
        """
        Get the trigger settings for this image.

        Returns:
            TriggerData: The trigger settings.
        """
        try:
            return self._image.Trigger
        except Exception as e:
            self.logger.error(f"Error getting trigger settings: {e}")
            return None

    @property
    def scale(self) -> None | str:
        # TEST:
        """
        Get or set the scale object.

        Returns:
            Scale: The scale object.
        """
        try:
            return self._image.Scale
        except Exception as e:
            self.logger.error(f"Error getting scale: {e}")
            return None

    @scale.setter
    def scale(self, value: str) -> None:
        # TEST:
        try:
            self._image.Scale = value
        except Exception as e:
            self.logger.error(f"Error setting scale: {e}")

    @property
    def palette_manager(self) -> None | str:
        # TEST:
        """
        Get the palette object.

        Returns:
            PaletteManager: The palette object.
        """
        try:
            return self._image.PaletteManager
        except Exception as e:
            self.logger.error(f"Error getting palette manager: {e}")
            return None

    @property
    def palette(self) -> None | str:
        # TEST:
        """
        Get or set the palette.

        Returns:
            Palette: The palette.
        """
        try:
            return self._image.Palette
        except Exception as e:
            self.logger.error(f"Error getting palette: {e}")
            return None

    @palette.setter
    def palette(self, value: str) -> None:
        # TEST:
        try:
            self._image.Palette = value
        except Exception as e:
            self.logger.error(f"Error setting palette: {e}")

    @property
    def isotherms(self) -> None | str:
        # TEST:
        """
        Get the collection of isotherms.

        Returns:
            IsothermCollection: The collection of isotherms.
        """
        try:
            return self._image.Isotherms
        except Exception as e:
            self.logger.error(f"Error getting isotherms: {e}")
            return None

    @property
    def alarms(self) -> None | str:
        # TEST:
        """
        Get the collection of alarms.

        Returns:
            AlarmCollectionManager: The collection of alarms.
        """
        try:
            return self._image.Alarms
        except Exception as e:
            self.logger.error(f"Error getting alarms: {e}")
            return None

    @property
    def fusion(self) -> None | str:
        # TEST:
        """
        Get the Fusion object.

        Returns:
            Fusion: The Fusion object.
        """
        try:
            return self._image.Fusion
        except Exception as e:
            self.logger.error(f"Error getting fusion: {e}")
            return None

    @property
    def image(self) -> None | str:
        # TEST:
        """
        Get the System.Drawing.Bitmap representing the image.

        Returns:
            Bitmap: The bitmap representing the image.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to get image.
        """
        try:
            return self._image.Image
        except Exception as e:
            self.logger.error(f"Error getting image: {e}")
            return None

    @property
    def date_time(self) -> None | str:
        # TEST:
        """
        Get or set the image creation UTC date and time.

        Returns:
            datetime: The image creation UTC date and time.
        """
        try:
            return self._image.DateTime
        except Exception as e:
            self.logger.error(f"Error getting date and time: {e}")
            return None

    @date_time.setter
    def date_time(self, value: str) -> None:
        # TEST:
        try:
            self._image.DateTime = value
        except Exception as e:
            self.logger.error(f"Error setting date and time: {e}")

    @property
    def date_taken(self) -> None | str:
        # TEST:
        """
        Get the date and time when the image was shot/taken.

        Returns:
            datetime: The date and time when the image was shot/taken.
        """
        try:
            return self._image.DateTaken
        except Exception as e:
            self.logger.error(f"Error getting date taken: {e}")
            return None

    @property
    def text_annotations(self) -> None | dict[str, str]:
        # TEST:
        """
        Get a collection of text annotation objects.

        Returns:
            dict: Text annotations as key-value pairs.
        """
        try:
            return self._image.TextAnnotations
        except Exception as e:
            self.logger.error(f"Error getting text annotations: {e}")
            return None

    @property
    def sensors_collection(self) -> None | str:
        # TEST:
        """
        Get a collection of sensor data objects.

        Returns:
            SensorsCollection: The collection of sensor data objects.
        """
        try:
            return self._image.SensorsCollection
        except Exception as e:
            self.logger.error(f"Error getting sensors collection: {e}")
            return None

    @property
    def voice_annotation(self) -> None | str:
        # TEST:
        """
        Get the voice annotation object.

        Returns:
            VoiceAnnotation: The voice annotation object.
        """
        try:
            return self._image.VoiceAnnotation
        except Exception as e:
            self.logger.error(f"Error getting voice annotation: {e}")
            return None

    """ PUBLIC MEMBER FUNCTIONS """

    def save_snapshot(self, filename: str, overlay: str = "") -> None:
        # TEST:
        """
        Save the current image to disk.

        Args:
            filename (str): The path to the location on which to save the file.
            overlay (Bitmap, optional): The jpeg representation of the Thermal image.

        Raises:
            System.ArgumentException: If the filename is null or empty.
            Flir.Atlas.Image.ThermalException: If failed to save Thermal image.
        """
        try:
            if overlay:
                self._image.SaveSnapshot(filename, overlay)
            else:
                self._image.SaveSnapshot(filename)
        except Exception as e:
            self.logger.error(f"Error saving snapshot: {e}")
            return None

    def dispose(self) -> None:
        # TEST:
        """
        Release all resources used by this Thermal-image.
        """
        try:
            self._image.Dispose()
        except Exception as e:
            self.logger.error(f"Error disposing Thermal image: {e}")
            return None

    def create(self, format_id: str, load_all: bool = True) -> None | bool:
        # TEST:
        """
        Create the underlying format (internal use).

        Args:
            format_id (str): The format ID.
            load_all (bool, optional): Whether to load all. Defaults to True.

        Returns:
            bool: True if creation is successful, otherwise False.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to create Thermal image.
        """
        try:
            return self._image.Create(format_id, load_all)
        except Exception as e:
            self.logger.error(f"Error creating Thermal image: {e}")
            return None

    def create_fff(self) -> None | bool:
        # TEST:
        """
        Create an empty image. This method is mainly for internal use.

        Returns:
            bool: True if creation is successful, otherwise False.
        """
        try:
            return self._image.CreateFFF()
        except Exception as e:
            self.logger.error(f"Error creating FFF image: {e}")
            return None

    def get_value_at(self, location: str) -> None | str:
        # TEST:
        """
        Get a ThermalValue from a position in the Thermal Image.

        Args:
            location (Point): A point that specifies the location for the value to read.

        Returns:
            ThermalValue: The ThermalValue including value and state.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to get value at the specified location.
        """
        try:
            return self._image.GetValueAt(location)
        except Exception as e:
            self.logger.error(f"Error getting value at location {location}: {e}")
            return None

    def get_signal_from_output(self, value: float) -> None | int:
        # TEST:
        """
        Extrapolate a signal value from an output value.

        Args:
            value (float): Value in current unit.

        Returns:
            int: Signal value.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to get signal from output value.
        """
        try:
            return self._image.GetSignalFromOutput(value)
        except Exception as e:
            self.logger.error(f"Error getting signal from output value {value}: {e}")
            return None

    def get_value_from_signal(self, signal: int) -> None | float:
        # TEST:
        """
        Get a temperature value from a signal.

        Args:
            signal (int): Signal value.

        Returns:
            float: Temperature value.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to get value from signal.
        """
        try:
            return self._image.GetValueFromSignal(signal)
        except Exception as e:
            self.logger.error(f"Error getting value from signal {signal}: {e}")
            return None

    def get_values(self, points: list[str]) -> None | list[float]:
        # TEST:
        """
        Get temperature values from an array of points.

        Args:
            points (list[Point]): A list of points which specifies the location for the value to read.

        Returns:
            list[float]: Temperature values.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to get values from points.
        """
        try:
            return self._image.GetValues(points)
        except Exception as e:
            self.logger.error(f"Error getting values from points {points}: {e}")
            return None

    def get_values_from_rectangle(self, rectangle: str) -> None | list[float]:
        # TEST:
        """
        Get temperatures from a signal.

        Args:
            rectangle (Rectangle): A rectangle which specifies the location for the value to be read.

        Returns:
            list[float]: Temperature values.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to get values from rectangle.
        """
        try:
            return self._image.GetValues(rectangle)
        except Exception as e:
            self.logger.error(f"Error getting values from rectangle {rectangle}: {e}")
            return None

    def get_values_by_reference(self, rectangle: str, data: list[float]) -> None:
        # TEST:
        """
        Get values by reference to data buffer.

        Args:
            rectangle (Rectangle): A rectangle which specifies the location for the value to be read.
            data (list[float]): Data buffer to store the values.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to get values by reference.
        """
        try:
            self._image.GetValues(rectangle, data)
        except Exception as e:
            self.logger.error(
                f"Error getting values by reference for rectangle {rectangle}: {e}"
            )
            return None

    def get_emissivity_from_value(
        self, temperature_measured: float, actual_temperature: float
    ) -> None | float:
        # TEST:
        """
        Calculate emissivity from a known temperature.

        Args:
            temperature_measured (float): The temperature measured in current TemperatureUnit.
            actual_temperature (float): The known temperature in current TemperatureUnit.

        Returns:
            float: A calculated emissivity value. Returns -1 if an error occurs.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to calculate emissivity.
        """
        try:
            return self._image.GetEmissivityFromValue(
                temperature_measured, actual_temperature
            )
        except Exception as e:
            self.logger.error(f"Error getting emissivity from value: {e}")
            return None

    def get_emissivity_from_value_at(
        self, x: int, y: int, actual_temperature: float
    ) -> None | float:
        # TEST:
        """
        Calculate emissivity from a known temperature at a specific position.

        Args:
            x (int): The temperature measured in current image at position x.
            y (int): The temperature measured in current image at position y.
            actual_temperature (float): The known temperature in current TemperatureUnit.

        Returns:
            float: A calculated emissivity value. Returns -1 if an error occurs.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to calculate emissivity.
        """
        try:
            return self._image.GetEmissivityFromValue(x, y, actual_temperature)
        except Exception as e:
            self.logger.error(
                f"Error getting emissivity from value at position ({x}, {y}): {e}"
            )
            return None

    def get_value_from_emissivity(
        self, emissivity: float, temperature: float
    ) -> None | float:
        # TEST:
        """
        Calculate temperature in current TemperatureUnit from emissivity.

        Args:
            emissivity (float): The known emissivity.
            temperature (float): The radiation as a signal value.

        Returns:
            float: A calculated temperature value.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to calculate temperature.
        """
        try:
            return self._image.GetValueFromEmissivity(emissivity, temperature)
        except Exception as e:
            self.logger.error(f"Error getting value from emissivity: {e}")
            return None

    def calculate_emissivity(
        self,
        radiation_measured: float,
        emissivity_measured: float,
        radiation_known: float,
        radiation_reflected: float,
    ) -> None | float:
        # TEST:
        """
        Calculate the emissivity from reference temperature.

        Args:
            radiation_measured (float): The temperature measured in current TemperatureUnit.
            emissivity_measured (float): The emissivity measured. If null then the emissivity of the image is used.
            radiation_known (float): The known temperature in current TemperatureUnit.
            radiation_reflected (float): The temperature ambient in current TemperatureUnit.

        Returns:
            float: A calculated emissivity value.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to calculate emissivity.
        """
        try:
            return self._image.CalculateEmissivity(
                radiation_measured,
                emissivity_measured,
                radiation_known,
                radiation_reflected,
            )
        except Exception as e:
            self.logger.error(f"Error calculating emissivity: {e}")
            return None

    def render_to(self, image_pixels: str) -> None:
        # TEST:
        """
        Render the new image to the input image buffer IPixels.

        Args:
            image_pixels (IPixels): Image buffer.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to render image.
        """
        try:
            self._image.RenderTo(image_pixels)
        except Exception as e:
            self.logger.error(f"Error rendering image to pixels: {e}")
            return None

    def image_array(self) -> None | list:
        # TEST:
        """
        Return a byte array representing the image.

        Returns:
            list: RGB byte array of the colorized image (3x8 bit).

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to get image array.
        """
        try:
            return self._image.ImageArray()
        except Exception as e:
            self.logger.error(f"Error getting image array: {e}")
            return None

    def rotate(self, angle: int) -> None | str:
        # TEST:
        """
        Rotate the image.

        Args:
            angle (int): The angle can be +- 90, 180 or 270 degrees.

        Returns:
            Bitmap: Rotated image.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to rotate image.
        """
        try:
            return self._image.Rotate(angle)
        except Exception as e:
            self.logger.error(f"Error rotating image by {angle} degrees: {e}")
            return None

    def set_rotate(self, angle: int) -> None:
        # TEST:
        """
        Rotate the image.

        Args:
            angle (int): The angle can be +- 90, 180 or 270 degrees.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to set rotate.
        """
        try:
            self._image.SetRotate(angle)
        except Exception as e:
            self.logger.error(f"Error setting rotate angle to {angle} degrees: {e}")
            return None

    def set_sketch(self, value: bool) -> None:
        # TEST:
        """
        Set sketch on or off.

        Args:
            value (bool): True to enable sketch, False to disable.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to set sketch.
        """
        try:
            self._image.SetSketch(value)
        except Exception as e:
            self.logger.error(f"Error setting sketch to {value}: {e}")
            return None

    def get_photo(self) -> None | str:
        # TEST:
        """
        Get the embedded photo.

        Returns:
            Bitmap: The embedded photo, null if not available.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to get photo.
        """
        try:
            return self._image.GetPhoto()
        except Exception as e:
            self.logger.error(f"Error getting photo: {e}")
            return None

    def copy(self, src: str) -> None:
        # TEST:
        """
        Copy a ThermalImage Measurements/Palette and Scale from source, it does not copy the pixel data.

        Args:
            src (ImageBase): ThermalImage to copy from.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to copy Thermal image.
        """
        try:
            self._image.Copy(src)
        except Exception as e:
            self.logger.error(f"Error copying Thermal image from source: {e}")
            return None

    """ PROTECTED MEMBER FUNCTIONS """

    def initialize(self) -> None:
        # TEST:
        """
        Initialize the Thermal Image.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to initialize Thermal image.
        """
        try:
            self._image.Initialize()
        except Exception as e:
            self.logger.error(f"Error initializing Thermal image: {e}")
            return None

    def setup_fusion(self) -> None:
        # TEST:
        """
        Check if the image contains Fusion data and set up event handling.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to set up Fusion.
        """
        try:
            self._image.SetupFusion()
        except Exception as e:
            self.logger.error(f"Error setting up Fusion: {e}")
            return None

    def set_color_distribution(self, value: str) -> None:
        # TEST:
        """
        Set color distribution.

        Args:
            value (ColorDistribution): The color distribution to set.

        Raises:
            ArgumentOutOfRangeException: If the argument is out of range.
        """
        try:
            self._image.SetColorDistribution(value)
        except Exception as e:
            self.logger.error(f"Error setting color distribution: {e}")
            return None

    def set_color_distribution_settings(self, value: str) -> None:
        # TEST:
        """
        Set color distribution settings.

        Args:
            value (ColorDistributionSettings): The color distribution settings to set.

        Raises:
            ArgumentOutOfRangeException: If the argument is out of range.
        """
        try:
            self._image.SetColorDistributionSettings(value)
        except Exception as e:
            self.logger.error(f"Error setting color distribution settings: {e}")
            return None

    def get_zoom_position(self, rect_pos: str, frame: str) -> None | str:
        # TEST:
        """
        Calculate the position of the rectangle in a zoomed-in image.

        Args:
            rect_pos (Rectangle): The rectangle in the image.
            frame (IFrame): The current frame.

        Returns:
            Rectangle: The position in the zoomed window.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to get zoom position.
        """
        try:
            return self._image.GetZoomPosition(rect_pos, frame)
        except Exception as e:
            self.logger.error(f"Error getting zoom position: {e}")
            return None

    def get_zoom_position_rotate(self, rect_pos: str, frame: str) -> None | str:
        # TEST:
        """
        Calculate the position of the rectangle in a zoomed-in image, not rotated.

        Args:
            rect_pos (Rectangle): The rectangle in the image.
            frame (IFrame): The current frame.

        Returns:
            Rectangle: The position in the zoomed window, not rotated.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to get zoom position.
        """
        try:
            return self._image.GetZoomPositionRotate(rect_pos, frame)
        except Exception as e:
            self.logger.error(f"Error getting zoom position rotate: {e}")
            return None

    def get_zoom_and_pan(self, frame: str) -> None | tuple[float, int, int]:
        # TEST:
        """
        Get the zoom and pan settings.

        Args:
            frame (IFrame): The current frame.

        Returns:
            tuple: The zoom factor, panX, and panY values.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to get zoom and pan settings.
        """
        try:
            zoom_factor, pan_x, pan_y = self._image.GetZoomAndPan(frame)
            return zoom_factor, pan_x, pan_y
        except Exception as e:
            self.logger.error(f"Error getting zoom and pan settings: {e}")
            return None

    def current_temperature_unit_changed(self, sender: object, e: str) -> None:
        # TEST:
        """
        Will be called whenever the temperature unit is changed.

        Args:
            sender (object): The sender.
            e (TemperatureUnitEventArgs): The temperature event argument.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to handle temperature unit change.
        """
        try:
            self._image.CurrentTemperature_UnitChanged(sender, e)
        except Exception as e:
            self.logger.error(f"Error handling temperature unit change: {e}")
            return None

    def raise_changed_event(self) -> None:
        # TEST:
        """
        Shall be raised for any changes made to the Thermal-image.

        Raises:
            Flir.Atlas.Image.ThermalException: If failed to raise changed event.
        """
        try:
            self._image.RaiseChangedEvent()
        except Exception as e:
            self.logger.error(f"Error raising changed event: {e}")
            return None

    def to_string(self) -> dict:
        """
        Return all properties in JSON format.

        Returns:
            str: JSON string of all properties.
        """

        properties = {
            "jpeg_image": str(self.jpeg_image),
            "overflow_signal_value": self.overflow_signal_value,
            "underflow_signal_value": self.underflow_signal_value,
            "min_signal_value": self.min_signal_value,
            "max_signal_value": self.max_signal_value,
            "precision": self.precision,
            "zoom": str(self.zoom),
            "color_distribution": str(self.color_distribution),
            "thermal_measurements": str(self.thermal_measurements),
            "statistics": str(self.statistics),
            "thermal_parameters": str(self.thermal_parameters),
            "temperature_unit": str(self.temperature_unit),
            "distance_unit": str(self.distance_unit),
            "camera_information": str(self.camera_information),
            "histogram": str(self.histogram),
            "measurements": str(self.measurements),
            "trigger": str(self.trigger),
            "scale": str(self.scale),
            "palette_manager": str(self.palette_manager),
            "palette": str(self.palette),
            "isotherms": str(self.isotherms),
            "alarms": str(self.alarms),
            "fusion": str(self.fusion),
            "image": str(self.image),
            "date_time": str(self.date_time),
            "date_taken": str(self.date_taken),
            "text_annotations": self.text_annotations,
            "sensors_collection": str(self.sensors_collection),
            "voice_annotation": str(self.voice_annotation),
        }

        return properties
