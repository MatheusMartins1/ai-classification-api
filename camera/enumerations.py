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


class CameraEnumerations:
    def __init__(self):
        "Camera Control enums"
        """1. Dual FOV Modes"""
        self.enum_dual_fov_mode_options = [
            {"name": "Wide", "value": 0, "description": "Wide field of view mode."},
            {
                "name": "Tele",
                "value": 1,
                "description": "Telephoto (narrow) field of view mode.",
            },
        ]

        """2. Focus Mode"""
        self.enum_focus_mode_options = [
            {"name": "Far", "value": 0, "description": "Focus set to far distance."},
            {"name": "Near", "value": 1, "description": "Focus set to near distance."},
            {"name": "Stop", "value": 2, "description": "Stop focus adjustment."},
            {"name": "Auto", "value": 3, "description": "Automatic focus adjustment."},
        ]

        """3. Camera Video Mode"""
        self.enum_video_mode_options = [
            {
                "name": "Pal",
                "value": 0,
                "description": "PAL video standard (commonly used in Europe and other regions).",
            },
            {
                "name": "Ntsc",
                "value": 1,
                "description": "NTSC video standard (commonly used in North America and other regions).",
            },
            {
                "name": "None",
                "value": 2,
                "description": "No specific video mode selected.",
            },
        ]

        """4. Scale Adjust Mode"""
        self.enum_scale_adjust_mode_options = [
            {
                "name": "Manual",
                "value": 0,
                "description": "Manual adjustment of the scale.",
            },
            {
                "name": "Auto",
                "value": 1,
                "description": "Automatic adjustment of the scale.",
            },
        ]

        """5. Windowing Mode"""
        self.enum_windowing_options = [
            {"name": "Off", "value": 0, "description": "Windowing mode disabled."},
            {
                "name": "Half",
                "value": 1,
                "description": "Windowing mode set to half resolution.",
            },
            {
                "name": "Quarter",
                "value": 2,
                "description": "Windowing mode set to quarter resolution.",
            },
        ]

        """6. Fusion Modes"""
        self.enum_fusion_mode_options = [
            {
                "name": "ThermalOnly",
                "value": 0,
                "description": "Thermal image shown as Thermal.",
            },
            {
                "name": "PictureInPicture",
                "value": 2,
                "description": "Thermal image shown as a photo with the Thermal image inside it.",
            },
            {
                "name": "Msx",
                "value": 3,
                "description": "Thermal image shown as MSX (Multi Spectral Dynamic Imaging).",
            },
            {
                "name": "VisualOnly",
                "value": 4,
                "description": "Thermal image shown as Visual image.",
            },
        ]

        "Image Enums"
        """7. Image Load Parameters"""
        self.enum_image_load_parameters_options = [
            {
                "name": "LoadNone",
                "value": 0x00000000,
                "description": "No parameters should be read from the frame.",
            },
            {
                "name": "LoadAlarms",
                "value": 0x00000001,
                "description": "Alarms should be read from the frame.",
            },
            {
                "name": "LoadImageFusion",
                "value": 0x00000002,
                "description": "Image fusion parameters should be read from the frame.",
            },
            {
                "name": "LoadIsotherms",
                "value": 0x00000004,
                "description": "Isotherms should be read from the frame.",
            },
            {
                "name": "LoadMeasurements",
                "value": 0x00000008,
                "description": "Measurements should be read from the frame.",
            },
            {
                "name": "LoadPalette",
                "value": 0x00000010,
                "description": "The palette should be read from the frame.",
            },
            {
                "name": "LoadTextAnnotations",
                "value": 0x00000020,
                "description": "Text annotations should be read from the frame.",
            },
            {
                "name": "LoadObjectParameters",
                "value": 0x00000040,
                "description": "Object parameters should be read from the frame.",
            },
            {
                "name": "LoadScale",
                "value": 0x00000080,
                "description": "Scale settings should be read from the frame.",
            },
            {
                "name": "LoadExternalSensors",
                "value": 0x00000100,
                "description": "External sensor data should be read from the frame.",
            },
            {
                "name": "LoadGPS",
                "value": 0x00000200,
                "description": "GPS data should be read from the frame.",
            },
            {
                "name": "LoadTemperatureUnit",
                "value": 0x00000400,
                "description": "Temperature unit should be read from the frame.",
            },
            {
                "name": "LoadRotateFlip",
                "value": 0x00000800,
                "description": "Rotate and flip settings should be read from the frame.",
            },
            {
                "name": "LoadAll",
                "value": 0xFFFFFFFF,
                "description": "All parameters should be read from the frame.",
            },
        ]

        """8. Temperature Unit"""
        self.enum_temperature_unit_options = [
            {
                "name": "Celsius",
                "value": 0,
                "description": "Unit in Celsius.The Celsius temperature scale was previously known as the centigrade scale.",
            },
            {"name": "Fahrenheit", "value": 1, "description": "Unit in Fahrenheit."},
            {
                "name": "Kelvin",
                "value": 2,
                "description": "Unit in Kelvin.The Kelvin scale is a thermodynamic (absolute) temperature scale where absolute zero, the theoretical absence of all thermal energy, is zero (0 K).",
            },
            {
                "name": "Signal",
                "value": 3,
                "description": "Unit in Signal (raw IR data).Signal is the actual value from the IR image not converted to a temperature. A signal value is not absolute; comparison between signal values from different images can be misleading.",
            },
        ]

        """9. Distance Unit"""
        self.enum_distance_unit_options = [
            {
                "name": "Meter",
                "value": 0,
                "description": "The meter is the fundamental unit of length in the International System of Units.",
            },
            {
                "name": "Feet",
                "value": 1,
                "description": "International foot (equal to 0.3048 meters).",
            },
        ]

        """10. Color Distribution"""
        self.enum_color_distribution_options = [
            {
                "name": "TemperatureLinear",
                "value": 0,
                "description": "This is an image-displaying method that distributes the colors according to temperature.",
            },
            {
                "name": "HistogramEqualization",
                "value": 1,
                "description": "This is an image-displaying method that evenly distributes the color information over the existing temperatures of the image. This method to distribute the information can be particularly successful when the image contains few peaks of very high temperature values.",
            },
            {
                "name": "SignalLinear",
                "value": 2,
                "description": "This is an image-displaying method where the color information in the image is distributed linear to the signal values of the pixels.",
            },
            {
                "name": "DigitalDetailEnhancement",
                "value": 3,
                "description": "DDE (Digital Detail Enhancement) is an advanced non linear image processing algorithm that preserves details in high dynamic range imagery. This detailed image is enhanced so that it matches the total dynamic range of the original image, thus making the details visible to the operator even in scenes with extreme temperature dynamics.",
            },
            {"name": "Ade", "value": 4, "description": "Adaptive detail enhancement."},
            {
                "name": "Entropy",
                "value": 5,
                "description": "Entropy modes reserve more shades of gray for areas with more entropy by assigning areas with lower entropy lesser gray shades.",
            },
            {
                "name": "PlateauHistogramEq",
                "value": 6,
                "description": "Perform a plateau histogram equalization.",
            },
            {
                "name": "GuidedFilterDDE",
                "value": 7,
                "description": "DDE (Digital Detail Enhancement) is an advanced non linear image processing algorithm that preserves details in high dynamic range imagery. This detailed image is enhanced so that it matches the total dynamic range of the original image, thus making the details visible to the operator even in scenes with extreme temperature dynamics.",
            },
            {
                "name": "Fsx",
                "value": 8,
                "description": "FSX/Digital Detail Enhancement (DDE 2.0).",
            },
        ]

        """11. Thermal Value State"""
        self.enum_thermal_value_state_options = [
            {
                "name": "Invalid",
                "value": 0,
                "description": "Value is invalid or could not be calculated.",
            },
            {"name": "None", "value": 1, "description": "Value is not yet calculated."},
            {"name": "Ok", "value": 2, "description": "Value is OK."},
            {"name": "Overflow", "value": 3, "description": "Value is too high."},
            {"name": "Underflow", "value": 4, "description": "Value is too low."},
            {"name": "Warning", "value": 5, "description": "Value is unreliable."},
        ]

        """12. Trigger Flags"""
        self.enum_trigger_flags_options = [
            {
                "name": "Valid",
                "value": 0x8000,
                "description": "Trig information is valid.",
            },
            {
                "name": "Triggered",
                "value": 0x0001,
                "description": "0=No trig, 1=Triggered.",
            },
            {
                "name": "Slope",
                "value": 0x0002,
                "description": "0=Negative, 1=Positive.",
            },
            {"name": "Type", "value": 0x0004, "description": "0=TTL, 1=OPTO."},
            {
                "name": "SerPort",
                "value": 0x0008,
                "description": "0=Negative, 1=Positive.",
            },
            {"name": "Start", "value": 0x0010, "description": "Start trig detected."},
            {"name": "Stop", "value": 0x0020, "description": "Stop trig detected."},
        ]

        """13. Visual Image Format"""
        self.enum_visual_image_format_options = [
            {"name": "Unknown", "value": 0, "description": "Unknown image format."},
            {"name": "Jpg", "value": 1, "description": "JPEG image format."},
            {"name": "Yuy2", "value": 2, "description": "YUY2 image format."},
            {"name": "Argb32", "value": 3, "description": "ARGB32 image format."},
        ]

        """14. Voice Annotation Format"""
        self.enum_voice_annotation_format_options = [
            {"name": "None", "value": 0, "description": "No sound format specified."},
            {"name": "Mp3", "value": 1, "description": "MP3 sound format."},
            {"name": "Wav", "value": 2, "description": "WAV sound format."},
        ]

        "Recorder enum"
        """1. RecorderState"""
        self.enum_recorder_state_options = [
            {"name": "Stopped", "value": 0, "description": "Recorder stopped."},
            {"name": "Paused", "value": 1, "description": "Recording paused."},
            {"name": "Recording", "value": 2, "description": "Recording started."},
        ]

        "Devide Enum"
        """1. Grabber State"""
        self.enum_grabber_state_options = [
            {
                "name": "NotReady",
                "value": 0,
                "description": "Camera is not ready to start streaming.",
            },
            {
                "name": "Cooling",
                "value": 1,
                "description": "Camera is busy cooling. Wait until Camera State is Ready before start streaming.",
            },
            {"name": "Ready", "value": 2, "description": "Ready for grabbing."},
        ]

        """2. Connection Status"""
        self.enum_connection_status_options = [
            {
                "name": "Disconnected",
                "value": 0,
                "description": "Device is disconnected.",
            },
            {
                "name": "Disconnecting",
                "value": 1,
                "description": "Device is disconnecting.",
            },
            {"name": "Connecting", "value": 2, "description": "Device is connecting."},
            {"name": "Connected", "value": 3, "description": "Device is connected."},
        ]

        """3. Dual Streaming Format"""
        self.enum_dual_streaming_format_options = [
            {
                "name": "Dual",
                "value": 0,
                "description": "The image is received as a thermal and a visual image.",
            },
            {
                "name": "Fusion",
                "value": 1,
                "description": "The image is received as a merged fusion image.",
            },
        ]

        """4. IO Type"""
        self.enum_io_type_options = [
            {"name": "Digital", "value": 0, "description": "Digital I/O port."},
            {"name": "Analog", "value": 1, "description": "Analog I/O port."},
        ]

        """5. IO Direction"""
        self.enum_io_direction_options = [
            {"name": "Input", "value": 0, "description": "Input pin."},
            {"name": "Output", "value": 1, "description": "Output pin."},
            {"name": "BiDirectional", "value": 2, "description": "Bi-directional pin."},
        ]

        """6. IO Polarity"""
        self.enum_io_polarity_options = [
            {"name": "ActiveHigh", "value": 0, "description": "Active high polarity."},
            {"name": "ActiveLow", "value": 1, "description": "Active low polarity."},
        ]

        """7. IO Sensitivity"""
        self.enum_io_sensitivity_options = [
            {
                "name": "RisingEdge",
                "value": 0,
                "description": "Rising edge sensitivity.",
            },
            {
                "name": "FallingEdge",
                "value": 1,
                "description": "Falling edge sensitivity.",
            },
            {
                "name": "Both",
                "value": 2,
                "description": "Both rising and falling edge sensitivity.",
            },
        ]

        """8. IO State"""
        self.enum_io_state_options = [
            {"name": "Deasserted", "value": 0, "description": "Deasserted state."},
            {"name": "Asserted", "value": 1, "description": "Asserted state."},
        ]

        """9. IO Config"""
        self.enum_io_config_options = [
            {
                "name": "GeneralPurpose",
                "value": 0,
                "description": "General purpose configuration.",
            },
            {
                "name": "VerticalSync",
                "value": 1,
                "description": "Vertical sync (output only).",
            },
            {
                "name": "SetMarkInIrImage",
                "value": 2,
                "description": "Set mark in IR image (input only).",
            },
            {
                "name": "SetStartMarkInIrImage",
                "value": 3,
                "description": "Set start mark in IR image (input only).",
            },
            {
                "name": "SetStopMarkInIrImage",
                "value": 4,
                "description": "Set stop mark in IR image (input only).",
            },
            {
                "name": "EnableImageFlow",
                "value": 5,
                "description": "Enable image flow (input only).",
            },
            {
                "name": "DisableImageFlow",
                "value": 6,
                "description": "Disable image flow (input only).",
            },
            {"name": "DisableNuc", "value": 7, "description": "Disable NUC."},
        ]

        """10. GenICam Type"""
        self.enum_gen_icam_type_options = [
            {"name": "Integer", "value": 0, "description": "Integer data type."},
            {"name": "Enum", "value": 1, "description": "Enum data type."},
            {"name": "Boolean", "value": 2, "description": "Boolean data type."},
            {"name": "String", "value": 3, "description": "String data type."},
            {"name": "Command", "value": 4, "description": "Command data type."},
            {"name": "Float", "value": 5, "description": "Float data type."},
        ]

        """11. Streaming Type"""
        self.enum_streaming_type_options = [
            {"name": "Unknown", "value": 0, "description": "Unknown streaming format."},
            {
                "name": "ThermalMono16",
                "value": 1,
                "description": "Thermal mono 16-bit format.",
            },
            {"name": "Jpg", "value": 2, "description": "Motion JPEG format."},
            {
                "name": "PpmArgb",
                "value": 3,
                "description": "PPM - Netpbm color image format.",
            },
            {"name": "Yuy2", "value": 4, "description": "YUY2 yuv pixel format."},
        ]

        "Discovery Enum"
        """1. Video Quality"""
        self.enum_video_quality_options = [
            {
                "name": "Default",
                "value": 0,
                "description": "Use default video quality.",
            },
            {"name": "High", "value": 1, "description": "Best quality possible."},
            {"name": "Medium", "value": 2, "description": "Average quality."},
            {
                "name": "Low",
                "value": 3,
                "description": "Save bandwidth, less quality in stream.",
            },
        ]

        """2. Interface"""
        self.enum_interface_options = [
            {"name": "None", "value": 0, "description": "None."},
            {
                "name": "Usb",
                "value": 0x00000001,
                "description": "USB port. T1K, EXX, T6XX, T4XX.",
            },
            {
                "name": "Network",
                "value": 0x00000002,
                "description": "Network adapter. A300, A310, AX8.",
            },
            {
                "name": "Firewire",
                "value": 0x00000004,
                "description": "Firewire port. P640.",
            },
            {
                "name": "Emulator",
                "value": 0x00000008,
                "description": "Emulating device interface.",
            },
            {
                "name": "Bluetooth",
                "value": 0x00000010,
                "description": "Bluetooth for wireless devices.",
            },
            {
                "name": "Gigabit",
                "value": 0x00000020,
                "description": "EBUS Gigabit camera. A615, A645, A655, A315, AX5.",
            },
            {
                "name": "Usb3",
                "value": 0x00000040,
                "description": "USB3 high speed camera. T1K with HSI interface.",
            },
            {
                "name": "Spinnaker",
                "value": 0x00000080,
                "description": "Spinnaker GigeVision camera e.g. A700, A500, A70.",
            },
            {
                "name": "All",
                "value": 0x7FFFFFFF,
                "description": "Flag used in Discovery.",
            },
            {
                "name": "Default",
                "value": 0x00000003,
                "description": "Default interfaces to scan (Network | Usb).",
            },
        ]

        """3. Image Format"""
        self.enum_image_format_options = [
            {
                "name": "FlirFileFormat",
                "value": 0,
                "description": "FLIR proprietary file and streaming format, 16-bit radiometric data used for temperature calculations.",
            },
            {
                "name": "Argb",
                "value": 1,
                "description": "32-bit ARGB with overlay from the camera.",
            },
            {
                "name": "Dual",
                "value": 2,
                "description": "FLIR proprietary file and streaming format, 16-bit radiometric data and 32-bit ARGB from the visual camera.",
            },
            {"name": "Unknown", "value": 3, "description": "Unknown streaming format."},
        ]

        """4. IP Config Error"""
        self.enum_ip_config_error_options = [
            {"name": "NoError", "value": 0, "description": "No error."},
            {"name": "NotConnected", "value": 1, "description": "Not connected."},
            {
                "name": "ConnectionFailed",
                "value": 2,
                "description": "Connection failed. Changing the IP settings might still be possible.",
            },
            {"name": "CameraNotFound", "value": 3, "description": "Camera not found."},
            {
                "name": "CameraLocked",
                "value": 4,
                "description": "Camera is in use by other application.",
            },
            {"name": "Unknown", "value": 5, "description": "Unknown error."},
        ]

        # Alarm
        self.enum_alarm_condition = [
            {
                "name": "Below",
                "value": 0,
                "description": "The alarms is trigged when the level is below a specified value.",
            },
            {
                "name": "Above",
                "value": 1,
                "description": "The alarms is trigged when the level is above a specified value.",
            },
            {
                "name": "Match",
                "value": 2,
                "description": "The alarms is trigged when the level matches a specified value.",
            },
            {
                "name": "Invalid",
                "value": 3,
                "description": "Indicates an invalid condition.",
            },
        ]

        self.enum_alarm_flags = [
            {"name": "None", "value": 0, "description": "No flags used."},
            {
                "name": "IsoIndication",
                "value": 1,
                "description": "The alarms has an isotherm indication.",
            },
            {
                "name": "IsoCoverage",
                "value": 2,
                "description": "The alarms uses an isotherm coverage.",
            },
        ]

        # TODO: Add GIGAVISION enums
        """Gigavision enums"""
        # self.enum_gigavision_options = []

        self.full_list = [
            {
                "enum": "DualFOVMode",
                "main_class": "Flir.Atlas.Live.Remote",
                "full_enum_path": "Flir.Atlas.Live.Remote.DualFOVMode",
                "description": "Dual FOV modes.",
                "options": self.enum_dual_fov_mode_options,
            },
            {
                "enum": "FocusMode",
                "main_class": "Flir.Atlas.Live.Remote",
                "full_enum_path": "Flir.Atlas.Live.Remote.FocusMode",
                "description": "Enumeration to set focus mode.",
                "options": self.enum_focus_mode_options,
            },
            {
                "enum": "VideoMode",
                "main_class": "Flir.Atlas.Live.Remote",
                "full_enum_path": "Flir.Atlas.Live.Remote.VideoMode",
                "options": self.enum_video_mode_options,
            },
            {
                "enum": "ScaleAdjustMode",
                "main_class": "Flir.Atlas.Live.Remote",
                "full_enum_path": "Flir.Atlas.Live.Remote.ScaleAdjustMode",
                "options": self.enum_scale_adjust_mode_options,
            },
            {
                "enum": "FusionMode",
                "main_class": "Flir.Atlas.Live.Remote",
                "full_enum_path": "Flir.Atlas.Live.Remote.FusionMode",
                "options": self.enum_fusion_mode_options,
            },
            {
                "enum": "Windowing",
                "main_class": "Flir.Atlas.Live.Remote",
                "full_enum_path": "Flir.Atlas.Live.Remote.Windowing",
                "options": self.enum_windowing_options,
            },
            {
                "enum": "ImageLoadParameters",
                "main_class": "Flir.Atlas.Image",
                "full_enum_path": "Flir.Atlas.Image.ImageLoadParameters",
                "options": self.enum_image_load_parameters_options,
            },
            {
                "enum": "TemperatureUnit",
                "main_class": "Flir.Atlas.Image",
                "full_enum_path": "Flir.Atlas.Image.TemperatureUnit",
                "options": self.enum_temperature_unit_options,
            },
            {
                "enum": "DistanceUnit",
                "main_class": "Flir.Atlas.Image",
                "full_enum_path": "Flir.Atlas.Image.DistanceUnit",
                "options": self.enum_distance_unit_options,
            },
            {
                "enum": "ColorDistribution",
                "main_class": "Flir.Atlas.Image",
                "full_enum_path": "Flir.Atlas.Image.ColorDistribution",
                "options": self.enum_color_distribution_options,
            },
            {
                "enum": "ThermalValueState",
                "main_class": "Flir.Atlas.Image",
                "full_enum_path": "Flir.Atlas.Image.ThermalValueState",
                "options": self.enum_thermal_value_state_options,
            },
            {
                "enum": "TriggerFlags",
                "main_class": "Flir.Atlas.Image",
                "full_enum_path": "Flir.Atlas.Image.TriggerFlags",
                "options": self.enum_trigger_flags_options,
            },
            {
                "enum": "VisualImageFormat",
                "main_class": "Flir.Atlas.Image",
                "full_enum_path": "Flir.Atlas.Image.VisualImageFormat",
                "options": self.enum_visual_image_format_options,
            },
            {
                "enum": "VoiceAnnotationFormat",
                "main_class": "Flir.Atlas.Image",
                "full_enum_path": "Flir.Atlas.Image.VoiceAnnotationFormat",
                "options": self.enum_voice_annotation_format_options,
            },
            {
                "enum": "RecorderState",
                "main_class": "Flir.Atlas.Live.Recorder",
                "full_enum_path": "Flir.Atlas.Live.Recorder.RecorderState",
                "options": self.enum_recorder_state_options,
            },
            {
                "enum": "ConnectionStatus",
                "main_class": "Flir.Atlas.Live.Device",
                "full_enum_path": "Flir.Atlas.Live.Device.ConnectionStatus",
                "description": "Connection status.",
                "options": self.enum_connection_status_options,
            },
            {
                "enum": "DualStreamingFormat",
                "main_class": "Flir.Atlas.Live.Device",
                "full_enum_path": "Flir.Atlas.Live.Device.DualStreamingFormat",
                "description": "Enumerate different dual streaming options.",
                "options": self.enum_dual_streaming_format_options,
            },
            {
                "enum": "GenICamType",
                "main_class": "Flir.Atlas.Live.Device",
                "full_enum_path": "Flir.Atlas.Live.Device.GenICamType",
                "description": "Data type.",
                "options": self.enum_gen_icam_type_options,
            },
            {
                "enum": "GrabberState",
                "main_class": "Flir.Atlas.Live.Device",
                "full_enum_path": "Flir.Atlas.Live.Device.GrabberState",
                "description": "Camera grabber state.",
                "options": self.enum_grabber_state_options,
            },
            {
                "enum": "IoConfig",
                "main_class": "Flir.Atlas.Live.Device",
                "full_enum_path": "Flir.Atlas.Live.Device.IoConfig",
                "description": "Port function configuration.",
                "options": self.enum_io_config_options,
            },
            {
                "enum": "IoDirection",
                "main_class": "Flir.Atlas.Live.Device",
                "full_enum_path": "Flir.Atlas.Live.Device.IoDirection",
                "description": "Type of I/O pin.",
                "options": self.enum_io_direction_options,
            },
            {
                "enum": "IoPolarity",
                "main_class": "Flir.Atlas.Live.Device",
                "full_enum_path": "Flir.Atlas.Live.Device.IoPolarity",
                "description": "Output port polarity.",
                "options": self.enum_io_polarity_options,
            },
            {
                "enum": "IoSensitivity",
                "main_class": "Flir.Atlas.Live.Device",
                "full_enum_path": "Flir.Atlas.Live.Device.IoSensitivity",
                "description": "Input port edge sensitivity (IOConfig 2,3",
                "options": self.enum_io_sensitivity_options,
            },
            {
                "enum": "IoState",
                "main_class": "Flir.Atlas.Live.Device",
                "full_enum_path": "Flir.Atlas.Live.Device.IoState",
                "description": "Current I/O port state.",
                "options": self.enum_io_state_options,
            },
            {
                "enum": "IoType",
                "main_class": "Flir.Atlas.Live.Device",
                "full_enum_path": "Flir.Atlas.Live.Device.IoType",
                "description": "Type of I/O port.",
                "options": self.enum_io_type_options,
            },
            {
                "enum": "StreamingType",
                "main_class": "Flir.Atlas.Live.Device",
                "full_enum_path": "Flir.Atlas.Live.Device.StreamingType",
                "description": "Types of streaming formats.",
                "options": self.enum_streaming_type_options,
            },
            {
                "enum": "ImageFormat",
                "main_class": "Flir.Atlas.Live.Discovery",
                "full_enum_path": "Flir.Atlas.Live.Discovery.ImageFormat",
                "description": "Enumeration of Image formats.",
                "options": self.enum_image_format_options,
            },
            {
                "enum": "Interface",
                "main_class": "Flir.Atlas.Live.Discovery",
                "full_enum_path": "Flir.Atlas.Live.Discovery.Interface",
                "description": "Interface flags.",
                "options": self.enum_interface_options,
            },
            {
                "enum": "IpConfigError",
                "main_class": "Flir.Atlas.Live.Discovery",
                "full_enum_path": "Flir.Atlas.Live.Discovery.IpConfigError",
                "description": "Error messages when using IP Config.",
                "options": self.enum_ip_config_error_options,
            },
            {
                "enum": "AlarmCondition",
                "main_class": "Flir.Atlas.Image.Alarms",
                "full_enum_path": "Flir.Atlas.Image.Alarms.AlarmCondition",
                "description": "Specifies the alarms conditions.",
                "options": self.enum_alarm_condition,
            },
            {
                "enum": "AlarmFlags",
                "main_class": "Flir.Atlas.Image.Alarms",
                "full_enum_path": "Flir.Atlas.Image.Alarms.AlarmFlags",
                "description": "Specifies the alarms flags.",
                "options": self.enum_alarm_flags,
            },
        ]

        self.links = [
            {
                "class": "Flir.Atlas.Image",
                "link": "https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/namespace_flir_1_1_atlas_1_1_image.html",
                "enum_done": True,
                "class_done": False,
                "tested": False,
            },
            {
                "class": "Flir.Atlas.Live.Device",
                "link": "https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/namespace_flir_1_1_atlas_1_1_live_1_1_device.html",
                "enum_done": True,
                "class_done": False,
                "tested": False,
            },
            {
                "class": "Flir.Atlas.Live.Discovery",
                "link": "https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/namespace_flir_1_1_atlas_1_1_live_1_1_discovery.html",
                "enum_done": True,
                "class_done": False,
                "tested": False,
            },
            {
                "class": "Flir.Atlas.Live.Recorder",
                "link": "https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/namespace_flir_1_1_atlas_1_1_live_1_1_recorder.html",
                "enum_done": True,
                "class_done": False,
                "tested": False,
            },
            {
                "class": "Flir.Atlas.Live.Remote",
                "link": "https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/namespace_flir_1_1_atlas_1_1_live_1_1_remote.html",
                "enum_done": True,
                "class_done": False,
                "tested": False,
            },
            {
                "class": "Flir.Atlas.Image.Alarms",
                "link": "https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/namespace_flir_1_1_atlas_1_1_image_1_1_alarms.html",
                "enum_done": False,
                "class_done": False,
                "tested": False,
            },
        ]
