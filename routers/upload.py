"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Router for handling file uploads from frontend application.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

import asyncio
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, Form, Header, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from config.api_key import verify_api_key
from utils.LoggerConfig import LoggerConfig

logger = LoggerConfig.add_file_logger(
    name="upload_router",
    filename=None,
    dir_name=None,
    prefix="upload",
    level_name="INFO",
)

from services import data_extractor_service

router = APIRouter(prefix="/api/v1", tags=["upload"])

# Ensure temp directory exists
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)


@router.post("/upload-inspection")
async def upload_inspection(
    request: Request,
    api_key: str = Depends(verify_api_key),
    company_id: Optional[str] = Header(None, alias="x-company-id"),
) -> JSONResponse:
    """
    Receive IR (infrared) images from frontend application.

    This endpoint handles the upload of thermal IR images sent as multipart/form-data
    with field names like ir_image_0, ir_image_1, etc.

    Metadata is received via HTTP headers with x- prefix.

    Args:
        request: FastAPI request object to access form data
        company_id: Company identifier (from header x-company-id)

    Returns:
        JSON response with processing status

    Raises:
        HTTPException: If validation fails or processing errors occur
    """
    try:
        # Parse multipart form data
        form_files = await request.form()

        # Build form_data dict from headers
        form_data = {
            "company_id": company_id or "",
        }

        logger.info(
            f"Recebendo upload de inspeção - Company: {company_id}, "
            f"Form fields: {list(form_files.keys())}"
        )

        # Extract IR image files (ir_image_0, ir_image_1, etc.)
        processed_ir_files: List[Dict] = []
        for field_name, field_value in form_files.items():
            if field_name.startswith("ir_image_"):
                # Check if it's a file by checking if it has file attributes
                if (
                    hasattr(field_value, "filename")
                    and hasattr(field_value, "read")
                    and hasattr(field_value, "content_type")
                ):
                    # Type narrowing: at this point we know it's an UploadFile
                    ir_file: UploadFile = field_value  # type: ignore

                    # Validate file type
                    if not ir_file.content_type or not ir_file.content_type.startswith(
                        "image/"
                    ):
                        logger.warning(
                            f"Arquivo IR inválido: {ir_file.filename} - "
                            f"{ir_file.content_type}"
                        )
                        continue

                    # Read file bytes
                    file_bytes = await ir_file.read()
                    file_size = len(file_bytes)

                    # Generate unique filename with timestamp
                    # TODO: Sobrescrevo a imagem ou mantenho um contador de imagens?
                    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    original_filename = ir_file.filename or "image.jpg"
                    image_name_splited = original_filename.split(".")
                    saved_filename = (
                        f"{image_name_splited[0]}_IR.{image_name_splited[1]}"
                    )
                    image_folder = os.path.join(TEMP_DIR, image_name_splited[0])
                    image_full_path = os.path.join(image_folder, saved_filename)
                    if os.path.exists(image_folder):
                        shutil.rmtree(image_folder)
                    os.makedirs(image_folder, exist_ok=True)

                    # Save image to temporary folder
                    with open(image_full_path, "wb") as f:
                        f.write(file_bytes)

                    processed_ir_files.append(
                        {
                            "field_name": field_name,
                            "filename": saved_filename,
                            "image_name": original_filename,
                            "content_type": ir_file.content_type,
                            "size": file_size,
                        }
                    )

                    logger.info(
                        f"Processado arquivo IR [{field_name}]: {saved_filename} "
                        f"({file_size} bytes) -> Salvo em: {image_full_path}"
                    )

        # Validate that we have at least one IR image
        if not processed_ir_files:
            raise HTTPException(
                status_code=400,
                detail="Pelo menos uma imagem infravermelha é obrigatória",
            )

        for index, image in enumerate(processed_ir_files):
            extracted_data = data_extractor_service.extract_data_from_image(
                image_name=image["image_name"],
                form_data=form_data,
            )
            processed_ir_files[index].update(extracted_data)

        # Build response
        response_data = {
            "status": "success",
            "message": "Imagens IR recebidas com sucesso",
            "company_info": {
                "company_id": form_data.get("company_id", ""),
            },
            "files_processed": len(processed_ir_files),
            "ir_images": processed_ir_files,
        }

        logger.info(f"Total imagens IR: {len(processed_ir_files)}")
        try:
            # Send data to storage and database without waiting for the response
            asyncio.create_task(
                data_extractor_service.send_data_to_storage(response_data)
            )
            logger.info(f"Dados enviados para o storage")

            # Send data to database
            from services.supabase_handler import SupabaseStorageHandler

            storage_handler = SupabaseStorageHandler()
            asyncio.create_task(storage_handler.send_data_to_database(response_data))
            logger.info(f"Dados enviados para o banco de dados")
        except Exception as e:
            logger.error(f"Erro ao enviar dados: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao enviar dados: {e}",
            )

        return JSONResponse(status_code=200, content=response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivos:")
