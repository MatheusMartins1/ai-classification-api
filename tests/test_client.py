"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Simple test client for the Image Metadata API.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

import os
import sys

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


def test_upload_inspection(image_path: str, user_id: str = "test_user_123"):
    """
    Test upload inspection endpoint with IR image.

    Sends the image exactly like the frontend does: using field name ir_image_0.

    Args:
        image_path: Path to IR image file
        user_id: User identifier for testing
    """
    if not os.path.exists(image_path):
        print(f"❌ Erro: Arquivo não encontrado: {image_path}")
        return

    filename = os.path.basename(image_path)
    file_size = os.path.getsize(image_path)
    print(f"📤 Enviando arquivo: {filename} ({file_size:,} bytes)")

    try:
        with open(image_path, "rb") as f:
            # Send with field name ir_image_0 (like frontend does)
            files = {"ir_image_0": (filename, f, "image/jpeg")}
            data = {
                "user_id": user_id,
                "company_id": "test_company_456",
                "email": "test@tenesso.com",
            }
            response = requests.post(
                "http://localhost:8345/api/v1/upload-inspection",
                files=files,
                data=data,
            )

        response_json = response.json()
        print(f"✅ Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Resposta: {result}")
            print(f"   - Arquivos processados: {result.get('files_processed', 0)}")
        else:
            print(f"❌ Erro: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor.")
        print(
            "   Certifique-se de que o servidor está rodando em http://localhost:8345"
        )
    except requests.exceptions.Timeout:
        print("❌ Erro: Timeout ao enviar arquivo (>30s)")
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")


if __name__ == "__main__":
    print("=" * 60)
    print("🔥 TESTE DE UPLOAD DE IMAGEM IR")
    print("=" * 60)

    # Check if image path was provided as argument
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Default image path
        image_path = "files/FLIR1970.jpg"

    test_upload_inspection(image_path)

    print("=" * 60)

    # Other tests (uncomment to use)
    # print("\n=== Testing Health ===")
    # test_health()
    # print("\n=== Testing Metadata Extraction ===")
    # test_extract_metadata("path/to/your/image.jpg")
