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

    temperature_unit: Optional[str] = Field(
        default="°C", description="Temperature unit"
    )
    temperature_unit_original: Optional[str] = Field(
        default="K", description="Temperature unit original"
    )
    emissivity: Optional[float] = Field(None, description="Surface emissivity")
    reflected_apparent_temperature: Optional[float] = Field(
        None, description="Reflected apparent temperature"
    )
    atmospheric_temperature: Optional[float] = Field(
        None, description="Atmospheric temperature"
    )
    relative_humidity: Optional[float] = Field(
        None, description="Relative humidity percentage"
    )
    ir_window_temperature: Optional[float] = Field(
        None, description="External optics temperature"
    )
    ir_window_transmission: Optional[float] = Field(
        None, description="External optics transmission"
    )
    temperature_range: Optional[str] = Field(
        None, description="Temperature range of the camera"
    )
    object_distance: Optional[float] = Field(
        None, description="Distance to object in meters"
    )
    camera_model: Optional[str] = Field(None, description="Camera model")
    camera_serial_number: Optional[str] = Field(
        None, description="Camera serial number"
    )
    lens_model: Optional[str] = Field(None, description="Lens model")
    filter_model: Optional[str] = Field(None, description="Filter model")
    date_time_original: Optional[str] = Field(
        None, description="Original capture datetime"
    )
    raw_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Raw metadata dictionary from flyr"
    )


class CameraMetadata(BaseModel):
    """Camera-specific metadata from FLIR thermal image."""

    camera_manufacturer: Optional[str] = Field(None, description="Camera manufacturer")
    camera_model: Optional[str] = Field(None, description="Camera model")
    camera_serial_number: Optional[str] = Field(
        None, description="Camera serial number"
    )
    lens_model: Optional[str] = Field(None, description="Lens model")
    lens_serial_number: Optional[str] = Field(None, description="Lens serial number")
    raw_camera_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Raw camera metadata dictionary"
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
        None, description="Raw EXIF metadata dictionary"
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
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
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
