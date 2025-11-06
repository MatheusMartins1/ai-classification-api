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


class CameraLocation:
    def __init__(self, _camera):
        self._camera = _camera
        self.logger = _camera.logger

        self.gps_info = None
        self.compass_info = None

        self.distance_unit = None
        self.object_distance = None

    def get_compass_info(self) -> None | Image.CompassInfo:
        """
        Get compass information from the camera.

        Returns:
            CompassInfo: The compass information.

        Raises:
            InvalidOperationException: If the operation is invalid.
        """
        try:
            return self._camera.RemoteControl.GeoLocation.GetCompassInfo()
        except Exception as e:
            self.logger.error(f"Error getting compass information: {e}")
            return None

    def get_gps_info(self) -> None | Image.GPSInfo:
        """
        Get GPS information from the camera.

        Returns:
            GPSInfo: The GPS information.

        Raises:
            InvalidOperationException: If GPS is not supported by the camera.
        """
        try:
            return self._camera.RemoteControl.GeoLocation.GetGpsInfo()
        except Exception as e:
            self.logger.error(f"Error getting GPS information: {e}")
            return None

    def gps_info_to_json(self, gps_info: Image.GPSInfo) -> dict:
        """
        Convert GPS information to a JSON serializable dictionary.

        Args:
            gps_info (GPSInfo): The GPS information.

        Returns:
            dict: The JSON serializable dictionary.
        """
        """
        Parameters
            altitude	Altitude
            altitudeRef	Indicates the altitude used as the reference altitude. If the reference is sea level and the altitude is above sea level, 0 is given. If the altitude is below sea level, a value of 1 is given and the altitude is indicated as an absolute value in Altitude. The reference unit is meters.
            dop	Indicates the GPS DOP (data degree of precision).
            latitude	Latitude
            latitudeRef	Indicates whether the latitude is north or south latitude. The value 'N' indicates north latitude, and 'S' is south latitude.
            longitude	Longitude
            longitudeRef	Indicates whether the longitude is east or west longitude. The value 'E' indicates east longitude, and 'W' is west longitude.
            mapDatum	Indicates the geodetic survey data used by the GPS receiver.
            satellites	Indicates the GPS satellites used for measurements. This tag can be used to describe the number of satellites, their ID number, angle of elevation, azimuth, SNR and other information in ASCII notation
            timestamp	Indicates the time as UTC (Coordinated Universal Time). Time is expressed as three values giving the hour, minute, and second. The format is HH:MM:SS.
        
        Properties
            bool 	IsValid[get, set]
                Gets a value indicating whether this GPSInfo is valid.
            
            double 	Altitude[get, set]
                Gets the altitude.
            
            long 	AltitudeRef[get, set]
                Gets the altitude reference.
            
            double 	Dop[get, set]
                Gets the DOP.
            
            double 	Latitude[get, set]
                Gets the latitude.
            
            string 	LatitudeRef[get, set]
                Gets the latitude reference.
            
            double 	Longitude[get, set]
                Gets the Longitude.
            
            string 	LongitudeRef[get, set]
                Gets the longitude reference.
            
            string 	MapDatum[get, set]
                Gets the map datum.
            
            string 	Satellites[get, set]
                Gets the satellites.
            
            long 	Timestamp[get, set]
                Gets time.
        """
        if gps_info:
            info = gps_info.ToString()

            info_dict = {
                "IsValid": gps_info.IsValid,
                "Altitude": gps_info.Altitude,
                "AltitudeRef": gps_info.AltitudeRef,
                "Dop": gps_info.Dop,
                "Latitude": gps_info.Latitude,
                "LatitudeRef": gps_info.LatitudeRef,
                "Longitude": gps_info.Longitude,
                "LongitudeRef": gps_info.LongitudeRef,
                "MapDatum": gps_info.MapDatum,
                "Satellites": gps_info.Satellites,
                "Timestamp": gps_info.Timestamp,
            }

            return info_dict

        return None


"""
TODO: Bring the following methods to the class above from control_settings.py?:
DISTANCE
https://update2flir2se.blob.core.windows.net/update/SSF/Atlas%20Cronos/docs/7.5.0/html/class_flir_1_1_atlas_1_1_live_1_1_remote_1_1_remote_camera_settings.html#a0f5085c7ee1228e27674160a4ea8b0e8
DistanceUnit 	GetDistanceUnit ()
 	Get distance unit used in the camera.
 
void 	SetDistanceUnit (DistanceUnit unit)
 	Set distance unit used in the camera.

     
double 	GetObjectDistance ()
 	Object distance (in meter). Range 0 - 10000.
 
void 	SetObjectDistance (double value)
 	Object distance (in meter). Range 0 - 10000.
"""
