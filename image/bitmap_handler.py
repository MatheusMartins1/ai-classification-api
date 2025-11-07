import datetime
import os

import clr
import cv2
import numpy as np
from PIL import Image

from config.settings import settings

clr.AddReference("System")

import System  # type: ignore
from System import Array, Byte  # type: ignore
from System.Drawing import Bitmap, Imaging  # type: ignore
from System.Runtime.InteropServices import Marshal  # type: ignore

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def get_bitmap_format(bitmap):
    """
    Retorna o formato do bitmap e o número de canais com base no PixelFormat do Bitmap.
    Possíveis valores retornados: ('argb', 4), ('rgb', 3), ('bgr', 3), ('rgba', 4), ('bgra', 4), ('abgr', 4).
    """
    pixel_format = bitmap.PixelFormat

    if pixel_format == Imaging.PixelFormat.Format32bppArgb:
        return "argb", 4
    elif pixel_format == Imaging.PixelFormat.Format24bppRgb:
        return "rgb", 3
    elif pixel_format == Imaging.PixelFormat.Format24bppBgr:
        return "bgr", 3
    elif pixel_format == Imaging.PixelFormat.Format32bppRgba:
        return "rgba", 4
    elif pixel_format == Imaging.PixelFormat.Format32bppBgra:
        return "bgra", 4
    elif pixel_format == Imaging.PixelFormat.Format32bppAbgr:
        return "abgr", 4
    else:
        raise ValueError(
            "Formato não suportado. Use ARGB (32bpp), RGB (24bpp), BGR (24bpp), RGBA (32bpp), BGRA (32bpp) ou ABGR (32bpp)."
        )


def bitmap_to_pil(bitmap):
    format_type, channels = get_bitmap_format(bitmap)
    pixel_format = bitmap.PixelFormat
    width = bitmap.Width
    height = bitmap.Height

    # Configura o PixelFormat e modo do PIL
    if format_type == "argb":
        pixel_format = Imaging.PixelFormat.Format32bppArgb
        pil_mode = "RGBA"  # PIL usa RGBA, mas ajustaremos a ordem dos bytes
        raw_mode = "BGRA"  # .NET armazena como BGRA
    else:
        pixel_format = Imaging.PixelFormat.Format24bppRgb
        pil_mode = "RGB"
        raw_mode = "BGR"  # .NET armazena como BGR

    # Bloqueia o bitmap para acesso aos pixels
    bitmap_data = bitmap.LockBits(
        System.Drawing.Rectangle(0, 0, width, height),
        Imaging.ImageLockMode.ReadOnly,
        pixel_format,
    )

    try:
        stride = bitmap_data.Stride
        buffer_size = height * stride
        buffer = bytearray(buffer_size)

        # Copia os bytes do .NET para o buffer
        # BUG: Error AccessViolationException
        clr.System.Runtime.InteropServices.Marshal.Copy(
            bitmap_data.Scan0, buffer, 0, buffer_size
        )

        # Converte para PIL Image
        pil_image = Image.frombytes(
            pil_mode,
            (width, height),
            bytes(buffer),
            "raw",
            raw_mode,  # Define a ordem dos bytes conforme o .NET
            stride,
            0,
        )

        # Se for ARGB, converte BGRA para RGBA (PIL espera RGBA)
        if format_type == "argb":
            pil_image = pil_image.convert("RGBA")

        return pil_image

    finally:
        bitmap.UnlockBits(bitmap_data)


def bitmap_to_cv2(bitmap):
    # Verifica se o bitmap é válido
    if not isinstance(bitmap, Bitmap):
        raise ValueError("Bitmap inválido ou já liberado.")

    # Configurações do bitmap
    width = bitmap.Width
    height = bitmap.Height

    rect = System.Drawing.Rectangle(0, 0, width, height)

    # Define o formato de pixel (ex: Format32bppArgb ou Format24bppRgb)
    pixel_format = bitmap.PixelFormat

    # Bloqueia o bitmap para acesso aos pixels
    bitmap_data = bitmap.LockBits(rect, Imaging.ImageLockMode.ReadOnly, pixel_format)

    stride = bitmap.Stride if hasattr(bitmap, "Stride") else bitmap_data.Stride
    is_inverted = stride < 0  # Imagem armazenada de ponta a cabeça

    try:

        if is_inverted:
            buffer_size = abs(stride) * height  # Tamanho total do buffer
        else:
            buffer_size = stride * height  # Tamanho total do buffer

        # Cria um buffer .NET (Array[Byte]) para garantir compatibilidade
        managed_buffer = Array.CreateInstance(Byte, buffer_size)

        # Copia os dados do Scan0 para o buffer .NET
        Marshal.Copy(bitmap_data.Scan0, managed_buffer, 0, buffer_size)

        # Converte o buffer .NET para bytes em Python
        buffer = bytes(managed_buffer)

        # Converte para array NumPy
        np_buffer = np.frombuffer(buffer, dtype=np.uint8)

        format_type, channels = get_bitmap_format(bitmap)

        if is_inverted:
            # Reshape considerando o stride absoluto
            np_buffer_original = np_buffer.reshape((height, abs(stride)))

            # Remove o padding se necessário (caso stride != width * channels)
            if abs(stride) != width * channels:
                np_buffer_original = np_buffer_original[:, : width * channels]

        np_buffer_original = np_buffer.reshape((height, width, channels))

        # Inverte a imagem verticalmente se o stride for negativo
        if is_inverted:
            np_buffer_original = np.flipud(np_buffer_original)

        a = 0
        r = 1
        g = 2
        b = 3

        if format_type == "argb":

            # ARGB -> BGRA (Blue, Green, Red, Alpha)
            np_buffer = np_buffer_original[
                :, :, [a, r, g, b]
            ]  # Extrai os canais na ordem B, G, R, A

            # np_buffer = np_buffer_original[:, :, [b, g, r, a]]  # Reordena os canais

        # elif format_type == "rgb":
        #     np_buffer = cv2.cvtColor(np_buffer_original, cv2.COLOR_BGR2RGB)
        else:
            np_buffer = np_buffer_original
        # elif format_type == "bgr":
        #     np_buffer = cv2.cvtColor(np_buffer_original, cv2.COLOR_BGR2RGB)
        # elif format_type == "rgba":
        #     np_buffer = cv2.cvtColor(np_buffer_original, cv2.COLOR_RGBA2BGRA)
        # elif format_type == "bgra":
        #     np_buffer = cv2.cvtColor(np_buffer_original, cv2.COLOR_BGRA2RGBA)
        # elif format_type == "abgr":
        #     np_buffer = cv2.cvtColor(np_buffer_original, cv2.COLOR_RGBA2BGRA)

        # cv2.imwrite(
        #         os.path.join(settings.BASE_DIR, "static_media","snapshots", f"test_image_argb.jpg"),
        #         np_buffer,
        #         [cv2.IMWRITE_JPEG_QUALITY, 90],
        # )

    except Exception as e:
        raise (f"Error converting .net image to cv2: {e}")

    finally:
        bitmap.UnlockBits(bitmap_data)

    return np_buffer
