"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Description: Service handler for Supabase storage operations with thermal image data.
Contact Email: matheus.sql18@gmail.com
All rights reserved.
"""

import asyncio
import os
import shutil
from typing import Any, Dict, List, Optional

from utils import temperature_calculations
from utils.LoggerConfig import LoggerConfig
from utils.supabase_client import SupabaseService

logger = LoggerConfig.add_file_logger(
    name="supabase_handler",
    filename=None,
    dir_name=None,
    prefix="supabase_handler",
    level_name="INFO",
)


class SupabaseStorageHandler:
    """
    Handler class for Supabase storage operations.
    Single responsibility: Manage thermal image file uploads to Supabase storage.
    """

    def __init__(self, bucket_name: str = "imagem") -> None:
        """
        Initialize Supabase storage handler.

        Args:
            bucket_name: Default bucket name for storage operations
        """
        self.supabase_service = SupabaseService()
        self.bucket_name = bucket_name

    async def send_data_to_storage(self, response_data: Dict[str, Any]) -> bool:
        """
        Save thermal image files to Supabase storage.

        Args:
            response_data: Dictionary containing IR images and user info

        Returns:
            True if all uploads succeed, False otherwise

        Raises:
            Exception: If upload fails
        """
        task_success = []

        for image in response_data["ir_images"]:
            storage_info = image.get("metadata", {}).get("storage_info", {})
            local_folder = storage_info.get("image_folder", "")
            company_id = response_data.get("user_info", {}).get("company_id", "")
            image_filename = storage_info.get("image_filename", "")
            content_type = image.get("content_type")

            # Upload IR and Real images
            files_to_upload = [
                storage_info.get("image_saved_ir_filename", ""),
                storage_info.get("image_saved_real_filename", ""),
            ]

            for filename in files_to_upload:
                success = await self._upload_file(
                    local_folder=local_folder,
                    filename=filename,
                    company_id=company_id,
                    image_filename=image_filename,
                    content_type=content_type,
                )
                task_success.append(success)

            # Upload temperature files
            for extension in ["csv", "json"]:
                filename = f"{image_filename}_temperature.{extension}"
                success = await self._upload_file(
                    local_folder=local_folder,
                    filename=filename,
                    company_id=company_id,
                    image_filename=image_filename,
                )
                task_success.append(success)

            # Upload metadata JSON
            filename_metadata = f"{image_filename}_metadata.json"
            success = await self._upload_file(
                local_folder=local_folder,
                filename=filename_metadata,
                company_id=company_id,
                image_filename=image_filename,
            )
            task_success.append(success)

        if all(task_success):
            # Remove temp folder after successful upload
            shutil.rmtree(local_folder)
            logger.info(
                f"Successfully uploaded all files and cleaned temp folder: {local_folder}"
            )
            return True
        else:
            logger.error("Some uploads failed. Temp folder not removed.")
            return False

    async def _upload_file(
        self,
        local_folder: str,
        filename: str,
        company_id: str,
        image_filename: str,
        content_type: Optional[str] = None,
    ) -> bool:
        """
        Upload a single file to Supabase storage.

        Args:
            local_folder: Local folder where file is stored
            filename: Name of the file to upload
            company_id: Company ID for storage path
            image_filename: Image filename for storage path
            content_type: Optional MIME type of the file

        Returns:
            True if upload succeeds, False otherwise
        """
        try:
            # Build storage path
            storage_path = "/".join(["companies", company_id, image_filename, filename])

            # Read file data
            local_file_path = os.path.join(local_folder, filename)
            with open(local_file_path, "rb") as f:
                file_data = f.read()

            # Upload to Supabase
            await asyncio.to_thread(
                self.supabase_service.upload_file,
                bucket_name=self.bucket_name,
                file_path=storage_path,
                file_data=file_data,
                content_type=content_type,
                if_exists="overwrite",
            )

            logger.info(f"Successfully uploaded: {storage_path}")
            return True

        except Exception as e:
            logger.error(f"Error uploading file {filename}: {e}")
            return False

    async def send_data_to_database(
        self, response_data: Dict[str, Any], table_name: str = "diagnosticos_mvp"
    ) -> bool:
        """
        Save thermal inspection data to Supabase database.

        Table Schema:
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

            -- Identificação
            id_anomalia        TEXT,
            tag          TEXT,
            nome_componente    TEXT,
            data_inspecao      DATE,

            -- Condições técnicas
            tipo_componente    TEXT,
            temperatura_maxima NUMERIC(5,2),
            temperatura_minima NUMERIC(5,2),
            delta_t            NUMERIC(5,2),
            mta                NUMERIC(5,2),
            desvio_padrao      NUMERIC(6,3),
            emissividade       NUMERIC(4,3),
            grau_severidade    TEXT,
            observacoes_tecnicas TEXT,

            -- Resultado IA
            diagnostico_ia     TEXT,
            recomendacao_ia    TEXT,

            -- Arquivos
            imagem_termica_url TEXT,     -- bucket: imagem (público)
            imagem_visual_url  TEXT,     -- bucket: imagem (público)
            arquivo_metadado_url TEXT,   -- bucket: metadado (privado, caminho completo)

            -- Controle
            criado_em          TIMESTAMPTZ DEFAULT now()

        Args:
            response_data: Dictionary containing IR images and metadata
            table_name: Name of the database table

        Returns:
            True if all inserts succeed, False otherwise
        """
        insert_success = []

        for image in response_data.get("ir_images", []):
            # Parse data for database insert
            db_record = self._parse_thermal_data_for_db(image, response_data)

            try:
                # Insert into database
                result = await asyncio.to_thread(
                    self.supabase_service.insert, table_name, db_record
                )
                logger.info(f"Successfully inserted record with id: {result.get('id')}")
                insert_success.append(True)
            except Exception as e:
                logger.error(f"Error inserting data to database: {e}")
                insert_success.append(False)

        return all(insert_success)

    def _parse_thermal_data_for_db(
        self, image_data: Dict[str, Any], response_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse thermal image data to match database schema.

        Args:
            image_data: Single thermal image data
            response_data: Complete response data with user info

        Returns:
            Dictionary matching database schema
        """
        metadata = image_data.get("metadata", {})
        storage_info = metadata.get("storage_info", {})
        calculations = metadata.get("calculations", {})
        flyr_metadata = metadata.get("flyr_metadata", {})
        company_id = response_data.get("user_info", {}).get("company_id", "")
        image_filename = storage_info.get("image_filename", "")
        exiftool_metadata = metadata.get("exiftool_metadata", {})

        # Build storage URLs
        base_path = f"companies/{company_id}/{image_filename}"
        imagem_termica_url = (
            f"{base_path}/{storage_info.get('image_saved_ir_filename', '')}"
        )
        imagem_visual_url = (
            f"{base_path}/{storage_info.get('image_saved_real_filename', '')}"
        )
        arquivo_metadado_url = f"{base_path}/{image_filename}_metadata.json"

        # Calculate severity grade
        delta_t = calculations.get("delta_t", 0.0)
        std_dev = calculations.get("standard_deviation", 0.0)
        severity_result = temperature_calculations.generate_severity_grade(
            delta_t=delta_t if delta_t else 0.0,
            std_dev=std_dev if std_dev else 0.0,
        )

        created_date = exiftool_metadata.get("create_date", "1900:01:01").replace(
            ":", "-"
        )[0:10]
        # Parse database record
        db_record = {
            # Identificação
            "id_anomalia": image_filename,
            "tag_ativo": storage_info.get("tag", ""),
            "nome_componente": None,  # TODO: Get from user input
            "data_inspecao": created_date,
            # Condições técnicas
            "tipo_componente": None,  # TODO: Get from user input
            "temperatura_maxima": self._round_decimal(
                calculations.get("max_temperature"), 2
            ),
            "temperatura_minima": self._round_decimal(
                calculations.get("min_temperature"), 2
            ),
            "delta_t": self._round_decimal(delta_t, 2),
            "mta": self._round_decimal(calculations.get("mta"), 2),
            "desvio_padrao": self._round_decimal(std_dev, 3),
            "emissividade": self._round_decimal(flyr_metadata.get("emissivity"), 3),
            "grau_severidade": severity_result.get("status"),
            "observacoes_tecnicas": " | ".join(severity_result.get("observations", [])),
            # Resultado IA
            "diagnostico_ia": None,  # TODO: Implement AI diagnosis
            "recomendacao_ia": None,  # TODO: Implement AI recommendation
            # Arquivos
            "imagem_termica_url": imagem_termica_url,
            "imagem_visual_url": imagem_visual_url,
            "arquivo_metadado_url": arquivo_metadado_url,
            "imagem_visual_nome": image_filename + "_REAL.jpg",
        }

        return db_record

    def _round_decimal(
        self, value: Optional[float], decimal_places: int
    ) -> Optional[float]:
        """
        Round decimal value to specified places.

        Args:
            value: Value to round
            decimal_places: Number of decimal places

        Returns:
            Rounded value or None
        """
        if value is None:
            return None
        try:
            return round(float(value), decimal_places)
        except (ValueError, TypeError):
            return None
