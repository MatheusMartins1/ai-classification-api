"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Service for extracting EXIF metadata using ExifTool.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

import platform
import subprocess
from typing import Any, Dict, Optional

from models.thermal_data import ExifToolMetadata
from utils.LoggerConfig import LoggerConfig

logger = LoggerConfig.add_file_logger(
    name="exiftool_extractor",
    filename=None,
    dir_name=None,
    prefix="exiftool",
    level_name="INFO",
)


class ExifToolExtractor:
    """
    Service class for extracting EXIF metadata using ExifTool.
    Single responsibility: Extract and parse EXIF data from thermal images.
    """

    def __init__(self, exiftool_path: str = "exiftool"):
        """
        Initialize ExifToolExtractor.

        Args:
            exiftool_path: Path to exiftool executable
        """
        self._is_windows = platform.system() == "Windows"
        if self._is_windows:
            exiftool_path = r"C:\Program Files\exiftool\exiftool.exe"
        else:
            exiftool_path = "exiftool"

        self.exiftool_path = exiftool_path

    def extract_metadata(self, image_path: str) -> Optional[ExifToolMetadata]:
        """
        Extract EXIF metadata from thermal image using ExifTool.

        Args:
            image_path: Path to the thermal image file

        Returns:
            ExifToolMetadata object or None if extraction fails
        """
        try:
            # Run exiftool command
            logger.info(f"Extracting EXIF metadata from: {image_path}")
            exif_data = self._run_exiftool(image_path)

            if not exif_data:
                logger.warning("No EXIF data extracted")
                return None

            # Parse and map to ExifToolMetadata
            metadata = self._parse_exif_data(exif_data)

            logger.info("Successfully extracted EXIF metadata")
            return metadata

        except Exception as e:
            logger.error(f"Error extracting EXIF metadata: {e}")
            return None

    def _run_exiftool(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        Run exiftool command and return parsed data.

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary with EXIF data or None
        """
        try:
            if self._is_windows:
                command = [self.exiftool_path, "-j", "-a", "-G", "-struct", image_path]
            else:
                command = ["exiftool", "-j", "-a", "-G", "-struct", image_path]

            # Run exiftool with JSON output
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                logger.error(f"ExifTool error: {result.stderr}")
                return None

            # Parse JSON output
            import json

            exif_list = json.loads(result.stdout)

            if not exif_list or len(exif_list) == 0:
                return None

            return exif_list[0]

        except subprocess.TimeoutExpired:
            logger.error("ExifTool command timed out")
            return None
        except FileNotFoundError:
            logger.error(
                f"ExifTool not found at: {self.exiftool_path}. "
                "Please install ExifTool or provide correct path."
            )
            return None
        except Exception as e:
            logger.error(f"Error running ExifTool: {e}")
            return None

    def _parse_exif_data(self, exif_data: Dict[str, Any]) -> ExifToolMetadata:
        """
        Parse raw EXIF data and map to ExifToolMetadata model.

        Args:
            exif_data: Raw EXIF data dictionary from ExifTool

        Returns:
            ExifToolMetadata object
        """

        # Helper function to get value with multiple possible keys
        def get_value(*keys):
            for key in keys:
                if key in exif_data:
                    return exif_data[key]
            return None

        # Helper function to parse float safely
        def safe_float(value):
            if value is None:
                return None
            try:
                return float(value)
            except (ValueError, TypeError):
                return None

        # Helper function to parse int safely
        def safe_int(value):
            if value is None:
                return None
            try:
                return int(value)
            except (ValueError, TypeError):
                return None

        metadata = ExifToolMetadata(
            # File Information
            file_name=get_value("File:FileName", "FileName"),
            file_size=safe_int(get_value("File:FileSize", "FileSize")),
            file_type=get_value("File:FileType", "FileType"),
            file_type_extension=get_value(
                "File:FileTypeExtension", "FileTypeExtension"
            ),
            mime_type=get_value("File:MIMEType", "MIMEType"),
            file_permissions=get_value("File:FilePermissions", "FilePermissions"),
            # Image Dimensions
            image_width=safe_int(
                get_value("File:ImageWidth", "ImageWidth", "EXIF:ImageWidth")
            ),
            image_height=safe_int(
                get_value("File:ImageHeight", "ImageHeight", "EXIF:ImageHeight")
            ),
            exif_image_width=safe_int(
                get_value("EXIF:ExifImageWidth", "ExifImageWidth")
            ),
            exif_image_height=safe_int(
                get_value("EXIF:ExifImageHeight", "ExifImageHeight")
            ),
            x_resolution=safe_float(get_value("EXIF:XResolution", "XResolution")),
            y_resolution=safe_float(get_value("EXIF:YResolution", "YResolution")),
            resolution_unit=get_value("EXIF:ResolutionUnit", "ResolutionUnit"),
            # Camera & Device Information
            make=get_value("EXIF:Make", "Make", "IFD0:Make"),
            camera_model_name=get_value(
                "EXIF:Model", "Model", "IFD0:Model", "CameraModelName"
            ),
            camera_serial_number=get_value(
                "APP1:CameraSerialNumber",
                "EXIF:SerialNumber",
                "SerialNumber",
                "CameraSerialNumber",
            ),
            lens_make=get_value("EXIF:LensMake", "LensMake"),
            lens_model=get_value("APP1:LensModel", "EXIF:LensModel", "LensModel"),
            lens_serial_number=get_value("EXIF:LensSerialNumber", "LensSerialNumber"),
            internal_serial_number=get_value(
                "EXIF:InternalSerialNumber", "InternalSerialNumber"
            ),
            # Date & Time
            create_date=get_value(
                "EXIF:CreateDate", "CreateDate", "File:FileModifyDate"
            ),
            modify_date=get_value(
                "EXIF:ModifyDate", "ModifyDate", "File:FileModifyDate"
            ),
            date_time_original=get_value(
                "EXIF:DateTimeOriginal", "DateTimeOriginal", "FLIR:DateTimeOriginal"
            ),
            sub_sec_time_original=get_value(
                "EXIF:SubSecTimeOriginal", "SubSecTimeOriginal"
            ),
            # Software & Processing
            software=get_value("EXIF:Software", "Software", "IFD0:Software"),
            creator_software=get_value("XMP:CreatorTool", "CreatorTool"),
            firmware_version=get_value(
                "EXIF:FirmwareVersion", "FirmwareVersion", "FLIR:FirmwareVersion"
            ),
            # GPS Location Data
            gps_version_id=get_value("GPS:GPSVersionID", "GPSVersionID"),
            gps_latitude_ref=get_value("GPS:GPSLatitudeRef", "GPSLatitudeRef"),
            gps_latitude=safe_float(get_value("GPS:GPSLatitude", "GPSLatitude")),
            gps_longitude_ref=get_value("GPS:GPSLongitudeRef", "GPSLongitudeRef"),
            gps_longitude=safe_float(get_value("GPS:GPSLongitude", "GPSLongitude")),
            gps_altitude_ref=get_value("GPS:GPSAltitudeRef", "GPSAltitudeRef"),
            gps_altitude=safe_float(get_value("GPS:GPSAltitude", "GPSAltitude")),
            gps_time_stamp=get_value("GPS:GPSTimeStamp", "GPSTimeStamp"),
            gps_satellites=get_value("GPS:GPSSatellites", "GPSSatellites"),
            gps_status=get_value("GPS:GPSStatus", "GPSStatus"),
            gps_measure_mode=get_value("GPS:GPSMeasureMode", "GPSMeasureMode"),
            gps_dop=safe_float(get_value("GPS:GPSDOP", "GPSDOP")),
            gps_speed_ref=get_value("GPS:GPSSpeedRef", "GPSSpeedRef"),
            gps_speed=safe_float(get_value("GPS:GPSSpeed", "GPSSpeed")),
            gps_track_ref=get_value("GPS:GPSTrackRef", "GPSTrackRef"),
            gps_track=safe_float(get_value("GPS:GPSTrack", "GPSTrack")),
            gps_img_direction_ref=get_value(
                "GPS:GPSImgDirectionRef", "GPSImgDirectionRef"
            ),
            gps_img_direction=safe_float(
                get_value("GPS:GPSImgDirection", "GPSImgDirection")
            ),
            gps_map_datum=get_value("GPS:GPSMapDatum", "GPSMapDatum"),
            gps_date_stamp=get_value("GPS:GPSDateStamp", "GPSDateStamp"),
            # FLIR Thermal Specific - Camera Settings
            camera_temperature_range_max=safe_float(
                get_value(
                    "APP1:CameraTemperatureRangeMax",
                    "FLIR:CameraTemperatureRangeMax",
                    "CameraTemperatureRangeMax",
                )
            ),
            camera_temperature_range_min=safe_float(
                get_value(
                    "APP1:CameraTemperatureRangeMin",
                    "FLIR:CameraTemperatureRangeMin",
                    "CameraTemperatureRangeMin",
                )
            ),
            camera_temperature_max_clip=safe_float(
                get_value(
                    "APP1:CameraTemperatureMaxClip",
                    "FLIR:CameraTemperatureMaxClip",
                    "CameraTemperatureMaxClip",
                )
            ),
            camera_temperature_min_clip=safe_float(
                get_value(
                    "APP1:CameraTemperatureMinClip",
                    "FLIR:CameraTemperatureMinClip",
                    "CameraTemperatureMinClip",
                )
            ),
            camera_temperature_max_warn=safe_float(
                get_value(
                    "APP1:CameraTemperatureMaxWarn",
                    "FLIR:CameraTemperatureMaxWarn",
                    "CameraTemperatureMaxWarn",
                )
            ),
            camera_temperature_min_warn=safe_float(
                get_value(
                    "APP1:CameraTemperatureMinWarn",
                    "FLIR:CameraTemperatureMinWarn",
                    "CameraTemperatureMinWarn",
                )
            ),
            camera_temperature_max_saturated=safe_float(
                get_value(
                    "APP1:CameraTemperatureMaxSaturated",
                    "FLIR:CameraTemperatureMaxSaturated",
                    "CameraTemperatureMaxSaturated",
                )
            ),
            camera_temperature_min_saturated=safe_float(
                get_value(
                    "APP1:CameraTemperatureMinSaturated",
                    "FLIR:CameraTemperatureMinSaturated",
                    "CameraTemperatureMinSaturated",
                )
            ),
            # FLIR Thermal Specific - Object Parameters
            emissivity=safe_float(
                get_value(
                    "APP1:Emissivity",
                    "MakerNotes:Emissivity",
                    "FLIR:Emissivity",
                    "Emissivity",
                )
            ),
            object_distance=safe_float(
                get_value(
                    "APP1:ObjectDistance", "FLIR:ObjectDistance", "ObjectDistance"
                )
            ),
            reflected_apparent_temperature=safe_float(
                get_value(
                    "APP1:ReflectedApparentTemperature",
                    "FLIR:ReflectedApparentTemperature",
                    "ReflectedApparentTemperature",
                )
            ),
            atmospheric_temperature=safe_float(
                get_value(
                    "APP1:AtmosphericTemperature",
                    "FLIR:AtmosphericTemperature",
                    "AtmosphericTemperature",
                )
            ),
            ir_window_temperature=safe_float(
                get_value(
                    "APP1:IRWindowTemperature",
                    "FLIR:IRWindowTemperature",
                    "IRWindowTemperature",
                )
            ),
            ir_window_transmission=safe_float(
                get_value(
                    "APP1:IRWindowTransmission",
                    "FLIR:IRWindowTransmission",
                    "IRWindowTransmission",
                )
            ),
            relative_humidity=safe_float(
                get_value(
                    "APP1:RelativeHumidity", "FLIR:RelativeHumidity", "RelativeHumidity"
                )
            ),
            atmospheric_trans_alpha1=safe_float(
                get_value(
                    "APP1:AtmosphericTransAlpha1",
                    "FLIR:AtmosphericTransAlpha1",
                    "AtmosphericTransAlpha1",
                )
            ),
            atmospheric_trans_alpha2=safe_float(
                get_value(
                    "APP1:AtmosphericTransAlpha2",
                    "FLIR:AtmosphericTransAlpha2",
                    "AtmosphericTransAlpha2",
                )
            ),
            atmospheric_trans_beta1=safe_float(
                get_value(
                    "APP1:AtmosphericTransBeta1",
                    "FLIR:AtmosphericTransBeta1",
                    "AtmosphericTransBeta1",
                )
            ),
            atmospheric_trans_beta2=safe_float(
                get_value(
                    "APP1:AtmosphericTransBeta2",
                    "FLIR:AtmosphericTransBeta2",
                    "AtmosphericTransBeta2",
                )
            ),
            atmospheric_trans_x=safe_float(
                get_value(
                    "APP1:AtmosphericTransX",
                    "FLIR:AtmosphericTransX",
                    "AtmosphericTransX",
                )
            ),
            # FLIR Thermal Specific - Planck Constants
            planck_r1=safe_float(
                get_value("APP1:PlanckR1", "FLIR:PlanckR1", "PlanckR1")
            ),
            planck_b=safe_float(get_value("APP1:PlanckB", "FLIR:PlanckB", "PlanckB")),
            planck_f=safe_float(get_value("APP1:PlanckF", "FLIR:PlanckF", "PlanckF")),
            planck_o=safe_int(get_value("APP1:PlanckO", "FLIR:PlanckO", "PlanckO")),
            planck_r2=safe_float(
                get_value("APP1:PlanckR2", "FLIR:PlanckR2", "PlanckR2")
            ),
            # FLIR Thermal Specific - Raw Sensor Data
            raw_thermal_image_width=safe_int(
                get_value("APP1:RawThermalImageWidth", "RawThermalImageWidth")
            ),
            raw_thermal_image_height=safe_int(
                get_value("APP1:RawThermalImageHeight", "RawThermalImageHeight")
            ),
            raw_thermal_image_type=get_value(
                "FLIR:RawThermalImageType", "RawThermalImageType"
            ),
            raw_value_range_min=safe_int(
                get_value("APP1:RawValueRangeMin", "RawValueRangeMin")
            ),
            raw_value_range_max=safe_int(
                get_value("APP1:RawValueRangeMax", "RawValueRangeMax")
            ),
            raw_value_median=safe_int(
                get_value("APP1:RawValueMedian", "RawValueMedian")
            ),
            raw_value_range=safe_int(get_value("APP1:RawValueRange", "RawValueRange")),
            # FLIR Thermal Specific - Palette & Display
            palette_colors=safe_int(get_value("APP1:PaletteColors", "PaletteColors")),
            above_color=get_value("APP1:AboveColor", "AboveColor"),
            below_color=get_value("APP1:BelowColor", "BelowColor"),
            overflow_color=get_value("APP1:OverflowColor", "OverflowColor"),
            underflow_color=get_value("APP1:UnderflowColor", "UnderflowColor"),
            isotherm1_color=get_value("APP1:Isotherm1Color", "Isotherm1Color"),
            isotherm2_color=get_value("APP1:Isotherm2Color", "Isotherm2Color"),
            palette_method=safe_int(get_value("APP1:PaletteMethod", "PaletteMethod")),
            palette_stretch=safe_int(
                get_value("APP1:PaletteStretch", "PaletteStretch")
            ),
            palette_file_name=get_value("APP1:PaletteFileName", "PaletteFileName"),
            # FLIR Thermal Specific - Focus & Lens
            focus_step_count=safe_int(
                get_value("APP1:FocusStepCount", "FocusStepCount")
            ),
            focus_distance=safe_float(get_value("APP1:FocusDistance", "FocusDistance")),
            field_of_view=safe_float(get_value("APP1:FieldOfView", "FieldOfView")),
            lens_part_number=get_value("APP1:LensPartNumber", "LensPartNumber"),
            # FLIR Thermal Specific - Calibration
            calibration_date=get_value("APP1:CalibrationDate", "CalibrationDate"),
            date_time_original_flir=get_value(
                "FLIR:DateTimeOriginal", "FLIRDateTimeOriginal"
            ),
            filter_model=get_value("APP1:FilterModel", "FilterModel"),
            filter_part_number=get_value("APP1:FilterPartNumber", "FilterPartNumber"),
            # FLIR Thermal Specific - Embedded Image
            embedded_image_width=safe_int(
                get_value("APP1:EmbeddedImageWidth", "EmbeddedImageWidth")
            ),
            embedded_image_height=safe_int(
                get_value("APP1:EmbeddedImageHeight", "EmbeddedImageHeight")
            ),
            embedded_image_type=get_value(
                "FLIR:EmbeddedImageType", "EmbeddedImageType"
            ),
            real_2_ir=get_value("APP1:Real2IR", "Real2IR"),
            # FLIR Thermal Specific - Measurement Tools
            marked_image=get_value("APP1:MarkedImage", "MarkedImage"),
            measurement_tool=get_value("APP1:MeasurementTool", "MeasurementTool"),
            # FLIR Thermal Specific - Offsets & Gains
            offset_x=safe_int(get_value("APP1:OffsetX", "OffsetX")),
            offset_y=safe_int(get_value("APP1:OffsetY", "OffsetY")),
            pip_x1=safe_int(get_value("APP1:PiPX1", "PiPX1")),
            pip_x2=safe_int(get_value("APP1:PiPX2", "PiPX2")),
            pip_y1=safe_int(get_value("APP1:PiPY1", "PiPY1")),
            pip_y2=safe_int(get_value("APP1:PiPY2", "PiPY2")),
            # FLIR Thermal Specific - App & Device Info
            app_version=get_value("APP1:AppVersion", "AppVersion"),
            file_source=get_value("EXIF:FileSource", "FileSource"),
            scene_capture_type=get_value("EXIF:SceneCaptureType", "SceneCaptureType"),
            # FLIR Thermal Specific - Misc
            subject_distance=safe_float(
                get_value("EXIF:SubjectDistance", "SubjectDistance")
            ),
            digital_zoom_ratio=safe_float(
                get_value("EXIF:DigitalZoomRatio", "DigitalZoomRatio")
            ),
            flash=get_value("EXIF:Flash", "Flash"),
            white_balance=get_value("EXIF:WhiteBalance", "WhiteBalance"),
            sharpness=get_value("EXIF:Sharpness", "Sharpness"),
            saturation=get_value("EXIF:Saturation", "Saturation"),
            contrast=get_value("EXIF:Contrast", "Contrast"),
            brightness=safe_float(get_value("EXIF:Brightness", "Brightness")),
            light_source=get_value("EXIF:LightSource", "LightSource"),
            exposure_mode=get_value("EXIF:ExposureMode", "ExposureMode"),
            exposure_program=get_value("EXIF:ExposureProgram", "ExposureProgram"),
            metering_mode=get_value("EXIF:MeteringMode", "MeteringMode"),
            # Color Space & Encoding
            color_space=get_value("EXIF:ColorSpace", "ColorSpace"),
            components_configuration=get_value(
                "EXIF:ComponentsConfiguration", "ComponentsConfiguration"
            ),
            y_cb_cr_positioning=get_value("EXIF:YCbCrPositioning", "YCbCrPositioning"),
            y_cb_cr_sub_sampling=get_value("EXIF:YCbCrSubSampling", "YCbCrSubSampling"),
            encoding_process=get_value("File:EncodingProcess", "EncodingProcess"),
            bits_per_sample=safe_int(get_value("EXIF:BitsPerSample", "BitsPerSample")),
            compression=get_value("EXIF:Compression", "Compression"),
            # Thumbnail
            thumbnail_offset=safe_int(
                get_value("IFD1:ThumbnailOffset", "ThumbnailOffset")
            ),
            thumbnail_length=safe_int(
                get_value("IFD1:ThumbnailLength", "ThumbnailLength")
            ),
            thumbnail_image=get_value("IFD1:ThumbnailImage", "ThumbnailImage"),
            # XMP & IPTC Metadata
            creator=get_value("XMP:Creator", "Creator", "IPTC:By-line"),
            rights=get_value("XMP:Rights", "Rights", "IPTC:CopyrightNotice"),
            description=get_value(
                "XMP:Description", "Description", "IPTC:Caption-Abstract"
            ),
            title=get_value("XMP:Title", "Title", "IPTC:ObjectName"),
            subject=get_value("XMP:Subject", "Subject", "IPTC:Keywords"),
            rating=safe_int(get_value("XMP:Rating", "Rating")),
            # Orientation
            orientation=get_value(
                "EXIF:Orientation", "Orientation", "IFD0:Orientation"
            ),
            # Raw metadata (excluded from JSON)
            raw_exif_metadata=exif_data,
        )
        
        return metadata
