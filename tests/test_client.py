"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Simple test client for the Image Metadata API.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

import requests


def test_health():
    """Test health endpoint."""
    response = requests.get("http://localhost:8345/health")
    print(f"Health Status: {response.status_code}")
    print(f"Response: {response.json()}")


def test_extract_metadata(image_path: str):
    """
    Test metadata extraction endpoint.

    Args:
        image_path: Path to image file
    """
    with open(image_path, "rb") as f:
        files = {"file": (image_path, f, "image/jpeg")}
        response = requests.post(
            "http://localhost:8345/api/v1/extract-metadata", files=files
        )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")


if __name__ == "__main__":
    # Test health
    print("=== Testing Health ===")
    test_health()

    # Test metadata extraction (uncomment and provide image path)
    # print("\n=== Testing Metadata Extraction ===")
    # test_extract_metadata("path/to/your/image.jpg")
