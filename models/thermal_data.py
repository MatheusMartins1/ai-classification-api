"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Data models for thermal image metadata from FLIR and ExifTool.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

from typing import Any, Dict, List, Optional

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
    """Metadata extracted from thermal image using ExifTool."""

    file_size: Optional[int] = Field(None, description="File size in bytes")
    file_type: Optional[str] = Field(None, description="File type")
    mime_type: Optional[str] = Field(None, description="MIME type")
    image_width: Optional[int] = Field(None, description="Image width in pixels")
    image_height: Optional[int] = Field(None, description="Image height in pixels")
    gps_latitude: Optional[float] = Field(None, description="GPS latitude")
    gps_longitude: Optional[float] = Field(None, description="GPS longitude")
    gps_altitude: Optional[float] = Field(None, description="GPS altitude")
    create_date: Optional[str] = Field(None, description="File creation date")
    modify_date: Optional[str] = Field(None, description="File modification date")
    software: Optional[str] = Field(None, description="Software used")
    raw_exif_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Raw EXIF metadata dictionary", exclude=True
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
    """Palette information if available."""

    # TODO: Implement this
    pass


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
