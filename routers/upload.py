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

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile
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
    user_id: str = Form(...),
    company_id: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    api_key: str = Depends(verify_api_key),
) -> JSONResponse:
    """
    Receive IR (infrared) images from frontend application.

    This endpoint handles the upload of thermal IR images sent as multipart/form-data
    with field names like ir_image_0, ir_image_1, etc.

    Args:
        request: FastAPI request object to access form data
        user_id: User identifier
        company_id: Company identifier (optional)
        email: User email (optional)

    Returns:
        JSON response with processing status

    Raises:
        HTTPException: If validation fails or processing errors occur
    """
    try:
        # Parse multipart form data
        form_data = await request.form()

        logger.info(
            f"Recebendo upload de inspeção - User: {user_id}, "
            f"Form fields: {list(form_data.keys())}"
        )

        # Extract IR image files (ir_image_0, ir_image_1, etc.)
        processed_ir_files: List[Dict] = []
        for field_name, field_value in form_data.items():
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
                tag=form_data.get("tag", ""),
            )
            processed_ir_files[index].update(extracted_data)

        # Build response
        response_data = {
            "status": "success",
            "message": "Imagens IR recebidas com sucesso",
            "user_info": {
                "user_id": user_id,
                "company_id": company_id,
                "email": email,
            },
            "files_processed": len(processed_ir_files),
            "ir_images": processed_ir_files,
        }

        logger.info(
            f"Upload concluído com sucesso - User: {user_id}, "
            f"Total imagens IR: {len(processed_ir_files)}"
        )
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
