"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Data models for thermal image metadata from FLIR and ExifTool.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class StorageInfo(BaseModel):
    """Storage information for thermal image files."""

    image_filename: str = Field(..., description="Base filename without extension")
    image_folder: str = Field(..., description="Folder path where image is stored")
    image_extension: str = Field(..., description="File extension")
    image_saved_ir_filename: str = Field(..., description="IR image filename")
    image_saved_real_filename: str = Field(
        ..., description="Real/optical image filename"
    )


class FlyrMetadata(BaseModel):
    """Metadata extracted from FLIR thermal image using flyr library."""

    # Temperature units
    temperature_unit: Optional[str] = Field(
        default="C", description="Temperature unit (standardized to C)"
    )
    temperature_unit_original: Optional[str] = Field(
        default="K", description="Original temperature unit from camera"
    )

    # Environmental parameters (converted to Celsius)
    emissivity: Optional[float] = Field(None, description="Surface emissivity (0-1)")
    object_distance: Optional[float] = Field(
        None, description="Distance to object in meters"
    )
    atmospheric_temperature: Optional[float] = Field(
        None, description="Atmospheric temperature in °C"
    )
    ir_window_temperature: Optional[float] = Field(
        None, description="External optics temperature in °C"
    )
    ir_window_transmission: Optional[float] = Field(
        None, description="External optics transmission (0-1)"
    )
    reflected_apparent_temperature: Optional[float] = Field(
        None, description="Reflected apparent temperature in °C"
    )
    relative_humidity: Optional[float] = Field(
        None, description="Relative humidity (0-1)"
    )

    # Planck constants (for raw temperature calculation)
    planck_r1: Optional[float] = Field(None, description="Planck R1 constant")
    planck_b: Optional[float] = Field(None, description="Planck B constant")
    planck_f: Optional[float] = Field(None, description="Planck F constant")
    planck_o: Optional[int] = Field(None, description="Planck O constant")
    atmospheric_trans_alpha1: Optional[float] = Field(
        None, description="Atmospheric transmission alpha 1"
    )
    atmospheric_trans_alpha2: Optional[float] = Field(
        None, description="Atmospheric transmission alpha 2"
    )
    atmospheric_trans_beta1: Optional[float] = Field(
        None, description="Atmospheric transmission beta 1"
    )
    atmospheric_trans_beta2: Optional[float] = Field(
        None, description="Atmospheric transmission beta 2"
    )
    atmospheric_trans_x: Optional[float] = Field(
        None, description="Atmospheric transmission X"
    )

    # Raw value ranges
    raw_value_range_min: Optional[int] = Field(
        None, description="Minimum raw sensor value"
    )
    raw_value_range_max: Optional[int] = Field(
        None, description="Maximum raw sensor value"
    )
    raw_value_median: Optional[int] = Field(None, description="Median raw sensor value")
    raw_value_range: Optional[int] = Field(
        None, description="Range of raw sensor values"
    )

    # Camera temperature ranges
    camera_temperature_range_max: Optional[float] = Field(
        None, description="Maximum camera temperature range"
    )
    camera_temperature_range_min: Optional[float] = Field(
        None, description="Minimum camera temperature range"
    )

    # Additional metadata (excluded from JSON export)
    raw_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Complete raw metadata dictionary from flyr", exclude=True
    )


class CameraMetadata(BaseModel):
    """Camera-specific metadata from FLIR thermal image."""

    # Resolution and file info
    resolution_unit: Optional[int] = Field(None, description="Resolution unit")
    exif_offset: Optional[int] = Field(None, description="EXIF offset in file")

    # Camera identification
    make: Optional[str] = Field(
        None, description="Camera manufacturer (FLIR Systems AB)"
    )
    model: Optional[str] = Field(None, description="Camera model (e.g., FLIR E60)")
    serial_number: Optional[str] = Field(None, description="Camera serial number")

    # Date and time
    date_time: Optional[str] = Field(None, description="Image capture date/time")

    # GPS data
    gps_data: Optional[Dict[str, Any]] = Field(None, description="GPS coordinates data")

    # Complete raw metadata (excluded from JSON export)
    raw_camera_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Complete raw camera metadata dictionary", exclude=True
    )


class ExifToolMetadata(BaseModel):
    """
    Complete EXIF metadata extracted from FLIR thermal image using ExifTool.
    Supports all standard EXIF, FLIR-specific, and GPS tags.
    """

    # ============================================================
    # FILE INFORMATION
    # ============================================================
    file_name: Optional[str] = Field(None, description="File name")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    file_type: Optional[str] = Field(None, description="File type (e.g., JPEG)")
    file_type_extension: Optional[str] = Field(None, description="File extension")
    mime_type: Optional[str] = Field(None, description="MIME type")
    file_permissions: Optional[str] = Field(None, description="File permissions")

    # ============================================================
    # IMAGE DIMENSIONS
    # ============================================================
    image_width: Optional[int] = Field(None, description="Image width in pixels")
    image_height: Optional[int] = Field(None, description="Image height in pixels")
    exif_image_width: Optional[int] = Field(None, description="EXIF image width")
    exif_image_height: Optional[int] = Field(None, description="EXIF image height")
    x_resolution: Optional[float] = Field(None, description="X resolution (DPI)")
    y_resolution: Optional[float] = Field(None, description="Y resolution (DPI)")
    resolution_unit: Optional[str] = Field(None, description="Resolution unit")

    # ============================================================
    # CAMERA & DEVICE INFORMATION
    # ============================================================
    make: Optional[str] = Field(None, description="Camera manufacturer")
    camera_model_name: Optional[str] = Field(None, description="Camera model")
    camera_serial_number: Optional[Union[str, int]] = Field(
        None, description="Camera serial number"
    )
    lens_make: Optional[str] = Field(None, description="Lens manufacturer")
    lens_model: Optional[str] = Field(None, description="Lens model")
    lens_serial_number: Optional[str] = Field(None, description="Lens serial number")
    internal_serial_number: Optional[str] = Field(
        None, description="Internal serial number"
    )

    # ============================================================
    # DATE & TIME
    # ============================================================
    create_date: Optional[str] = Field(None, description="File creation date")
    modify_date: Optional[str] = Field(None, description="File modification date")
    date_time_original: Optional[str] = Field(
        None, description="Original capture date/time"
    )
    sub_sec_time_original: Optional[str] = Field(
        None, description="Subsecond time original"
    )

    # ============================================================
    # SOFTWARE & PROCESSING
    # ============================================================
    software: Optional[str] = Field(None, description="Software used")
    creator_software: Optional[str] = Field(None, description="Creator software")
    firmware_version: Optional[str] = Field(None, description="Firmware version")

    # ============================================================
    # GPS LOCATION DATA
    # ============================================================
    gps_version_id: Optional[str] = Field(None, description="GPS version ID")
    gps_latitude_ref: Optional[str] = Field(
        None, description="GPS latitude reference (N/S)"
    )
    gps_latitude: Optional[float] = Field(None, description="GPS latitude (decimal)")
    gps_longitude_ref: Optional[str] = Field(
        None, description="GPS longitude reference (E/W)"
    )
    gps_longitude: Optional[float] = Field(None, description="GPS longitude (decimal)")
    gps_altitude_ref: Optional[str] = Field(
        None, description="GPS altitude reference (above/below sea level)"
    )
    gps_altitude: Optional[float] = Field(None, description="GPS altitude in meters")
    gps_time_stamp: Optional[str] = Field(None, description="GPS time stamp")
    gps_satellites: Optional[str] = Field(None, description="GPS satellites used")
    gps_status: Optional[str] = Field(None, description="GPS receiver status")
    gps_measure_mode: Optional[str] = Field(None, description="GPS measurement mode")
    gps_dop: Optional[float] = Field(None, description="GPS dilution of precision")
    gps_speed_ref: Optional[str] = Field(None, description="GPS speed reference")
    gps_speed: Optional[float] = Field(None, description="GPS speed")
    gps_track_ref: Optional[str] = Field(None, description="GPS track reference")
    gps_track: Optional[float] = Field(None, description="GPS track")
    gps_img_direction_ref: Optional[str] = Field(
        None, description="GPS image direction reference"
    )
    gps_img_direction: Optional[float] = Field(None, description="GPS image direction")
    gps_map_datum: Optional[str] = Field(None, description="GPS map datum")
    gps_date_stamp: Optional[str] = Field(None, description="GPS date stamp")

    # ============================================================
    # FLIR THERMAL SPECIFIC - CAMERA SETTINGS
    # ============================================================
    camera_temperature_range_max: Optional[float] = Field(
        None, description="Camera temperature range maximum"
    )
    camera_temperature_range_min: Optional[float] = Field(
        None, description="Camera temperature range minimum"
    )
    camera_temperature_max_clip: Optional[float] = Field(
        None, description="Camera temperature max clip"
    )
    camera_temperature_min_clip: Optional[float] = Field(
        None, description="Camera temperature min clip"
    )
    camera_temperature_max_warn: Optional[float] = Field(
        None, description="Camera temperature max warning"
    )
    camera_temperature_min_warn: Optional[float] = Field(
        None, description="Camera temperature min warning"
    )
    camera_temperature_max_saturated: Optional[float] = Field(
        None, description="Camera temperature max saturated"
    )
    camera_temperature_min_saturated: Optional[float] = Field(
        None, description="Camera temperature min saturated"
    )

    # ============================================================
    # FLIR THERMAL SPECIFIC - OBJECT PARAMETERS
    # ============================================================
    emissivity: Optional[float] = Field(None, description="Object emissivity")
    object_distance: Optional[float] = Field(
        None, description="Distance to object in meters"
    )
    reflected_apparent_temperature: Optional[float] = Field(
        None, description="Reflected apparent temperature"
    )
    atmospheric_temperature: Optional[float] = Field(
        None, description="Atmospheric temperature"
    )
    ir_window_temperature: Optional[float] = Field(
        None, description="IR window temperature"
    )
    ir_window_transmission: Optional[float] = Field(
        None, description="IR window transmission"
    )
    relative_humidity: Optional[float] = Field(None, description="Relative humidity")
    atmospheric_trans_alpha1: Optional[float] = Field(
        None, description="Atmospheric transmission alpha 1"
    )
    atmospheric_trans_alpha2: Optional[float] = Field(
        None, description="Atmospheric transmission alpha 2"
    )
    atmospheric_trans_beta1: Optional[float] = Field(
        None, description="Atmospheric transmission beta 1"
    )
    atmospheric_trans_beta2: Optional[float] = Field(
        None, description="Atmospheric transmission beta 2"
    )
    atmospheric_trans_x: Optional[float] = Field(
        None, description="Atmospheric transmission X"
    )

    # ============================================================
    # FLIR THERMAL SPECIFIC - PLANCK CONSTANTS
    # ============================================================
    planck_r1: Optional[float] = Field(None, description="Planck R1 constant")
    planck_b: Optional[float] = Field(None, description="Planck B constant")
    planck_f: Optional[float] = Field(None, description="Planck F constant")
    planck_o: Optional[int] = Field(None, description="Planck O constant")
    planck_r2: Optional[float] = Field(None, description="Planck R2 constant")

    # ============================================================
    # FLIR THERMAL SPECIFIC - RAW SENSOR DATA
    # ============================================================
    raw_thermal_image_width: Optional[int] = Field(
        None, description="Raw thermal image width"
    )
    raw_thermal_image_height: Optional[int] = Field(
        None, description="Raw thermal image height"
    )
    raw_thermal_image_type: Optional[str] = Field(
        None, description="Raw thermal image type"
    )
    raw_value_range_min: Optional[int] = Field(
        None, description="Raw value range minimum"
    )
    raw_value_range_max: Optional[int] = Field(
        None, description="Raw value range maximum"
    )
    raw_value_median: Optional[int] = Field(None, description="Raw value median")
    raw_value_range: Optional[int] = Field(None, description="Raw value range")

    # ============================================================
    # FLIR THERMAL SPECIFIC - PALETTE & DISPLAY
    # ============================================================
    palette_colors: Optional[int] = Field(None, description="Number of palette colors")
    above_color: Optional[str] = Field(None, description="Above color (Y Cb Cr)")
    below_color: Optional[str] = Field(None, description="Below color (Y Cb Cr)")
    overflow_color: Optional[str] = Field(None, description="Overflow color (Y Cb Cr)")
    underflow_color: Optional[str] = Field(
        None, description="Underflow color (Y Cb Cr)"
    )
    isotherm1_color: Optional[str] = Field(
        None, description="Isotherm 1 color (Y Cb Cr)"
    )
    isotherm2_color: Optional[str] = Field(
        None, description="Isotherm 2 color (Y Cb Cr)"
    )
    palette_method: Optional[int] = Field(None, description="Palette method")
    palette_stretch: Optional[int] = Field(None, description="Palette stretch")
    palette_file_name: Optional[str] = Field(None, description="Palette file name")

    # ============================================================
    # FLIR THERMAL SPECIFIC - FOCUS & LENS
    # ============================================================
    focus_step_count: Optional[int] = Field(None, description="Focus step count")
    focus_distance: Optional[float] = Field(None, description="Focus distance")
    field_of_view: Optional[float] = Field(None, description="Field of view")
    lens_part_number: Optional[str] = Field(None, description="Lens part number")

    # ============================================================
    # FLIR THERMAL SPECIFIC - CALIBRATION
    # ============================================================
    calibration_date: Optional[str] = Field(None, description="Calibration date")
    date_time_original_flir: Optional[str] = Field(
        None, description="FLIR original date/time"
    )
    filter_model: Optional[str] = Field(None, description="Filter model")
    filter_part_number: Optional[str] = Field(None, description="Filter part number")

    # ============================================================
    # FLIR THERMAL SPECIFIC - EMBEDDED IMAGE
    # ============================================================
    embedded_image_width: Optional[int] = Field(
        None, description="Embedded image width"
    )
    embedded_image_height: Optional[int] = Field(
        None, description="Embedded image height"
    )
    embedded_image_type: Optional[str] = Field(None, description="Embedded image type")
    real_2_ir: Optional[Union[str, float]] = Field(
        None, description="Real to IR transformation ratio"
    )

    # ============================================================
    # FLIR THERMAL SPECIFIC - MEASUREMENT TOOLS
    # ============================================================
    marked_image: Optional[str] = Field(None, description="Marked image flag")
    measurement_tool: Optional[str] = Field(None, description="Measurement tool used")

    # ============================================================
    # FLIR THERMAL SPECIFIC - OFFSETS & GAINS
    # ============================================================
    offset_x: Optional[int] = Field(None, description="Offset X")
    offset_y: Optional[int] = Field(None, description="Offset Y")
    pip_x1: Optional[int] = Field(None, description="Picture-in-Picture X1")
    pip_x2: Optional[int] = Field(None, description="Picture-in-Picture X2")
    pip_y1: Optional[int] = Field(None, description="Picture-in-Picture Y1")
    pip_y2: Optional[int] = Field(None, description="Picture-in-Picture Y2")

    # ============================================================
    # FLIR THERMAL SPECIFIC - APP & DEVICE INFO
    # ============================================================
    app_version: Optional[str] = Field(None, description="Application version")
    file_source: Optional[str] = Field(None, description="File source")
    scene_capture_type: Optional[str] = Field(None, description="Scene capture type")

    # ============================================================
    # FLIR THERMAL SPECIFIC - MISC
    # ============================================================
    subject_distance: Optional[float] = Field(None, description="Subject distance")
    digital_zoom_ratio: Optional[float] = Field(None, description="Digital zoom ratio")
    flash: Optional[str] = Field(None, description="Flash setting")
    white_balance: Optional[str] = Field(None, description="White balance")
    sharpness: Optional[str] = Field(None, description="Sharpness")
    saturation: Optional[str] = Field(None, description="Saturation")
    contrast: Optional[str] = Field(None, description="Contrast")
    brightness: Optional[float] = Field(None, description="Brightness")
    light_source: Optional[str] = Field(None, description="Light source")
    exposure_mode: Optional[str] = Field(None, description="Exposure mode")
    exposure_program: Optional[str] = Field(None, description="Exposure program")
    metering_mode: Optional[str] = Field(None, description="Metering mode")

    # ============================================================
    # COLOR SPACE & ENCODING
    # ============================================================
    color_space: Optional[str] = Field(None, description="Color space")
    components_configuration: Optional[str] = Field(
        None, description="Components configuration"
    )
    y_cb_cr_positioning: Optional[str] = Field(None, description="YCbCr positioning")
    y_cb_cr_sub_sampling: Optional[str] = Field(None, description="YCbCr sub-sampling")
    encoding_process: Optional[str] = Field(None, description="Encoding process")
    bits_per_sample: Optional[int] = Field(None, description="Bits per sample")
    compression: Optional[str] = Field(None, description="Compression type")

    # ============================================================
    # THUMBNAIL
    # ============================================================
    thumbnail_offset: Optional[int] = Field(None, description="Thumbnail offset")
    thumbnail_length: Optional[int] = Field(None, description="Thumbnail length")
    thumbnail_image: Optional[str] = Field(None, description="Thumbnail image data")

    # ============================================================
    # XMP & IPTC METADATA
    # ============================================================
    creator: Optional[str] = Field(None, description="Creator/Author")
    rights: Optional[str] = Field(None, description="Copyright/Rights")
    description: Optional[str] = Field(None, description="Image description")
    title: Optional[str] = Field(None, description="Image title")
    subject: Optional[str] = Field(None, description="Subject/Keywords")
    rating: Optional[int] = Field(None, description="Image rating")

    # ============================================================
    # ORIENTATION
    # ============================================================
    orientation: Optional[str] = Field(None, description="Image orientation")

    # ============================================================
    # RAW METADATA
    # ============================================================
    raw_exif_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Complete raw EXIF metadata dictionary"
    )


class Measurement(BaseModel):
    """
    Measurement data from thermal image.
    Based on flyr.measurement_info.Measurement class.
    """

    type: Optional[str] = Field(
        None,
        description="Measurement type (SPOT, AREA, LINE, RECTANGLE, ELLIPSE, CIRCLE, POLYGON)",
    )
    x: Optional[int] = Field(None, description="X coordinate")
    y: Optional[int] = Field(None, description="Y coordinate")
    width: Optional[int] = Field(None, description="Width")
    height: Optional[int] = Field(None, description="Height")

    # Temperature statistics
    temperature: Optional[float] = Field(
        None, description="Average temperature in Celsius"
    )
    min_temperature: Optional[float] = Field(None, description="Minimum temperature")
    max_temperature: Optional[float] = Field(None, description="Maximum temperature")
    median_temperature: Optional[float] = Field(None, description="Median temperature")
    std_deviation: Optional[float] = Field(None, description="Standard deviation")
    variance: Optional[float] = Field(None, description="Variance")
    percentile_25: Optional[float] = Field(None, description="25th percentile")
    percentile_75: Optional[float] = Field(None, description="75th percentile")
    percentile_90: Optional[float] = Field(None, description="90th percentile")

    # Visual properties
    color: Optional[str] = Field(None, description="Color")
    label: Optional[str] = Field(None, description="Label")
    description: Optional[str] = Field(None, description="Description")
    notes: Optional[str] = Field(None, description="Notes")


class TemperatureData(BaseModel):
    """Temperature matrix data from thermal image."""

    celsius: List[List[float]] = Field(
        ..., description="2D temperature matrix in Celsius"
    )
    min_temperature: Optional[float] = Field(
        None, description="Minimum temperature in image"
    )
    max_temperature: Optional[float] = Field(
        None, description="Maximum temperature in image"
    )
    avg_temperature: Optional[float] = Field(
        None, description="Average temperature in image"
    )
    median_temperature: Optional[float] = Field(
        None, description="Median temperature in image"
    )
    delta_t: Optional[float] = Field(None, description="Delta T in image")


class PipInfo(BaseModel):
    """Picture-in-Picture information if available."""

    pip_x: Optional[int] = Field(None, description="PIP X coordinate")
    pip_y: Optional[int] = Field(None, description="PIP Y coordinate")
    pip_width: Optional[int] = Field(None, description="PIP width")
    pip_height: Optional[int] = Field(None, description="PIP height")


class PaletteInfo(BaseModel):
    """Palette/color map information from thermal image."""

    # Color definitions
    above_color: Optional[tuple] = Field(
        None, description="RGB color for values above range (r, g, b)"
    )
    below_color: Optional[tuple] = Field(
        None, description="RGB color for values below range (r, g, b)"
    )
    overflow_color: Optional[tuple] = Field(
        None, description="RGB color for overflow values (r, g, b)"
    )
    underflow_color: Optional[tuple] = Field(
        None, description="RGB color for underflow values (r, g, b)"
    )
    isotherm1_color: Optional[tuple] = Field(
        None, description="RGB color for isotherm 1 (r, g, b)"
    )
    isotherm2_color: Optional[tuple] = Field(
        None, description="RGB color for isotherm 2 (r, g, b)"
    )

    # Palette properties
    method: Optional[int] = Field(None, description="Palette method/algorithm")
    name: Optional[str] = Field(None, description="Palette name")
    num_colors: Optional[int] = Field(None, description="Number of colors in palette")
    stretch: Optional[int] = Field(None, description="Palette stretch factor")

    # File reference
    file_name: Optional[str] = Field(None, description="Palette file name")
    path: Optional[str] = Field(None, description="Path to palette file")

    # RGB values array
    rgb_values: Optional[List[tuple]] = Field(
        None, description="Array of RGB tuples for each color in palette"
    )

    # YCbCr values array (if available)
    yccs: Optional[List[tuple]] = Field(
        None, description="Array of YCbCr tuples for each color"
    )


class ThermalImageData(BaseModel):
    """
    Complete thermal image data model.
    Combines data from FLIR (flyr library) and ExifTool extraction.
    """

    storage_info: StorageInfo = Field(..., description="Storage information")
    flyr_metadata: Optional[FlyrMetadata] = Field(
        None, description="Metadata from flyr library"
    )
    camera_metadata: Optional[CameraMetadata] = Field(
        None, description="Camera-specific metadata"
    )
    exiftool_metadata: Optional[ExifToolMetadata] = Field(
        None, description="Metadata from ExifTool"
    )
    temperature_data: Optional[TemperatureData] = Field(
        None, description="Temperature matrix data"
    )
    measurements: Optional[List[Measurement]] = Field(
        None, description="List of measurements from thermal image"
    )
    pip_info: Optional[PipInfo] = Field(
        None, description="Picture-in-Picture information"
    )
    palette_info: Optional[PaletteInfo] = Field(
        None, description="Palette/color map information"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "storage_info": {
                    "image_filename": "FLIR1970",
                    "image_folder": "temp/FLIR1970",
                    "image_extension": "jpg",
                    "image_saved_ir_filename": "FLIR1970_IR.jpg",
                    "image_saved_real_filename": "FLIR1970_REAL.jpg",
                },
                "flyr_metadata": {
                    "emissivity": 0.95,
                    "reflected_apparent_temperature": 20.0,
                    "atmospheric_temperature": 20.0,
                    "relative_humidity": 50.0,
                    "temperature_range": "[-20.0, 120.0]",
                },
                "temperature_data": {
                    "celsius": [[25.5, 26.0], [25.8, 26.2]],
                    "min_temperature": 25.5,
                    "max_temperature": 26.2,
                    "avg_temperature": 25.875,
                },
            }
        }
