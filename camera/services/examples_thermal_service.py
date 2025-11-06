"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

"""
Examples of how to use the DataExtractorService in your views.
"""


# Example 1: Complete thermal data extraction
def example_complete_data_extraction(thermal_image):
    """Example of extracting complete thermal data."""
    from camera.services.data_extractor import get_thermal_data_for_view

    # Get all thermal data
    result = get_thermal_data_for_view(thermal_image, "complete")

    # Result will be:
    # {
    #     "status": "success",
    #     "message": "Thermal data extracted successfully (complete)",
    #     "data": {
    #         "ImageMetadata": {...},
    #         "CameraInformation": {...},
    #         "GpsInformation": {...},
    #         "CompassInformation": {...},
    #         "ThermalParameters": {...},
    #         "GasQuantification": {...},
    #         "ZoomInformation": {...},
    #         "Statistics": {...}
    #     },
    #     "requested_type": "complete",
    #     "data_keys": ["ImageMetadata", "CameraInformation", ...]
    # }

    return result


# Example 2: Specific data type extraction
def example_specific_data_extraction(thermal_image):
    """Example of extracting specific thermal data types."""
    from camera.services.data_extractor import get_thermal_data_for_view

    # Get only GPS data
    gps_result = get_thermal_data_for_view(thermal_image, "gps")

    # Result will be:
    # {
    #     "status": "success",
    #     "message": "Thermal data extracted successfully (gps)",
    #     "data": {
    #         "data_type": "gps",
    #         "data": {
    #             "IsValid": true,
    #             "Latitude": 40.7128,
    #             "Longitude": -74.0060,
    #             "Altitude": 10.5,
    #             ...
    #         }
    #     },
    #     "requested_type": "gps"
    # }

    # Get only camera data
    camera_result = get_thermal_data_for_view(thermal_image, "camera")

    return gps_result, camera_result


# Example 3: Data validation
def example_data_validation():
    """Example of validating data types before extraction."""
    from camera.services.data_extractor import validate_thermal_data_request

    # Valid data types
    valid_types = [
        "complete",
        "gps",
        "camera",
        "thermal_params",
        "gas",
        "compass",
        "zoom",
        "statistics",
        "metadata",
    ]

    for data_type in valid_types:
        is_valid, message = validate_thermal_data_request(data_type)
        print(f"{data_type}: {is_valid} - {message}")

    # Invalid data type
    is_valid, message = validate_thermal_data_request("invalid_type")
    print(f"invalid_type: {is_valid} - {message}")


# Example 4: Error handling
def example_error_handling(thermal_image):
    """Example of proper error handling."""
    from camera.services.data_extractor import get_thermal_data_for_view

    result = get_thermal_data_for_view(thermal_image, "gps")

    if result["status"] == "error":
        print(f"Error: {result['message']}")
        return None

    # Successful extraction
    thermal_data = result["data"]
    return thermal_data


# Example 5: Integration with Django view (like your get_thermal_data)
def example_django_view_integration(request_or_message, camera):
    """Example of how to integrate with your Django view."""
    from camera.services.data_extractor import (
        get_thermal_data_for_view,
        validate_thermal_data_request,
    )
    from django.http import JsonResponse

    # Extract parameters (similar to your view)
    if hasattr(request_or_message, "GET"):
        thermal_image = camera.get_thermal_image()
        data_to_extract = request_or_message.GET.get("data_to_extract", "complete")
    else:
        payload = request_or_message.get("payload", {})
        thermal_image = camera.get_thermal_image(format=payload.get("format", "Dual"))
        data_to_extract = payload.get("data_to_extract", "complete")

    # Validate thermal image
    if thermal_image is None:
        return JsonResponse({"error": "No thermal image available"}, status=404)

    # Validate data type
    is_valid, validation_message = validate_thermal_data_request(data_to_extract)
    if not is_valid:
        return JsonResponse({"error": validation_message}, status=400)

    # Extract data
    result = get_thermal_data_for_view(thermal_image, data_to_extract)

    # Return response
    status_code = 200 if result["status"] == "success" else 500
    return JsonResponse(result, status=status_code)


# Example 6: Available data types
def example_available_data_types():
    """Example of getting available data types."""
    from camera.services.data_extractor import DataExtractorService

    available_types = DataExtractorService.get_available_data_types()

    print("Available thermal data types:")
    for data_type, description in available_types.items():
        print(f"  {data_type}: {description}")


# Example 7: Testing different data extractions
def example_test_all_data_types(thermal_image):
    """Test extracting all available data types."""
    from camera.services.data_extractor import (
        get_thermal_data_for_view,
        DataExtractorService,
    )

    available_types = DataExtractorService.get_available_data_types()
    results = {}

    for data_type in available_types.keys():
        try:
            result = get_thermal_data_for_view(thermal_image, data_type)
            results[data_type] = {
                "success": result["status"] == "success",
                "message": result["message"],
                "has_data": result["data"] is not None,
            }
        except Exception as e:
            results[data_type] = {
                "success": False,
                "message": str(e),
                "has_data": False,
            }

    return results


if __name__ == "__main__":
    print("Thermal Data Extractor Service Examples")
    print("=" * 50)

    # Show available data types
    example_available_data_types()

    # Show validation examples
    print("\nValidation Examples:")
    example_data_validation()
