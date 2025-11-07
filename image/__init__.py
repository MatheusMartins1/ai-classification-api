"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

# Import from the image_data_extraction module for backward compatibility
from image.image_data_extraction import (
    extract_all_attributes,
    safe_extract_attribute,
    extract_image_metadata,
    extract_gps_information,
    extract_camera_information,
    extract_gas_quantification_result,
    extract_gas_quantification_input,
    extract_compass_information,
    extract_thermal_parameters,
    # Note: other extraction functions exist but are incomplete in the source
)

# Export all for external use
__all__ = [
    "extract_all_attributes",
    "safe_extract_attribute",
    "extract_image_metadata",
    "extract_gps_information",
    "extract_camera_information",
    "extract_gas_quantification_result",
    "extract_gas_quantification_input",
    "extract_compass_information",
    "extract_thermal_parameters",
]
